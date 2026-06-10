# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################

from __future__ import annotations

import os
import re
import shlex
import subprocess
import tempfile
from collections.abc import Generator
from glob import glob

from PySide6 import QtCore

from .responses import ExecuteResponse, AssembleResponse


class _FakeSocket(QtCore.QObject):
    """Dummy socket-like object to satisfy debug signal connections in mainwindow."""
    sentLine: QtCore.Signal = QtCore.Signal(str)
    receivedLine: QtCore.Signal = QtCore.Signal(str)


class ARMSimModuleConnector(QtCore.QObject):
    """In-process ARMSim connector.

    Presents the same public API as ARMSimConnector but communicates
    directly with MainServer (qtarmsim.armsim) instead of via a
    subprocess / TCP socket.
    """

    # Regular expressions (shared with ARMSimConnector)
    re_regexpr: re.Pattern[str] = re.compile("r([0-9]+): (0[xX][0-9a-fA-F]+)")
    re_membanksexpr: re.Pattern[str] = re.compile(
        "([^.:]+).*(0[xX][0-9A-Fa-f]*).*-.*(0[xX][0-9A-Fa-f]*)"
    )
    re_memexpr: re.Pattern[str] = re.compile("(0[xX][0-9a-fA-F]+): (0[xX][0-9a-fA-F]+)")

    stdoutLine: QtCore.Signal = QtCore.Signal(str)

    def __init__(self, verbose: bool = False) -> None:
        super().__init__()
        self.verbose: bool = verbose
        # Dummy socket object so debug code in mainwindow can connect signals
        self.mySocket = _FakeSocket()
        self._server = None
        self._connected: bool = False
        self.version: str = ''
        self.messages: list[str] = []
        self._settings: dict[str, str] = {}
        self._updateTimer: QtCore.QTimer = QtCore.QTimer()
        _ = self._updateTimer.timeout.connect(self.doUpdate)
        self._updateTimer.start(1000)

    # ── Connection management ────────────────────────────────────────────

    def setConnected(self, connected: bool, port: int | None = None) -> None:
        self._connected = connected

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def currentPort(self) -> int | None:
        return None  # No port for in-process connector

    def connectTo(
        self, _command: str, _working_directory: str, _server: str, _port: int
    ) -> str | None:
        """Initialise the in-process simulator.

        The command / working_directory / server / port arguments are
        accepted for API compatibility but ignored.

        @return: error message on failure, None on success.
        """
        from ..armsim.armsim_module.server import MainServer
        from ..armsim.armsim_module.core import Core
        from ..armsim.armsim_module.read_elf import read_elf, ORIG_CODE, END_DATA
        from ..armsim.armsim_module import thumb2_defs as T

        firmware_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', 'armsim', 'armsim_module', 'Firmware.o')
        )
        try:
            blocks = read_elf(firmware_path, firmware=True)
        except Exception as e:
            return "Could not load firmware from '{}':\n    {}".format(firmware_path, e)

        procesador = Core(T.ARCH, blocks[0])
        procesador.memory().add_block(blocks[1])
        procesador.memory().symbol_table = blocks[2]
        T._symbol_table = blocks[2]
        T._use_symbols = False
        procesador.update({'usr_regs': [T.PC, ORIG_CODE, T.SP, END_DATA - 128]})

        firm_table = {k: v for k, v in blocks[2].items() if blocks[3].get(k) == 1}

        self._server = MainServer(procesador, 0)
        self._server._firm_table = firm_table
        self._server._firmware_block = blocks[0]

        self.setConnected(True)
        return None

    def disconnect_from(self) -> None:
        if self._server is not None:
            self._server.process("EXIT")
        self._server = None
        self.setConnected(False)

    def doUpdate(self) -> None:
        # No subprocess stdout to drain; just keep the timer running.
        self._updateTimer.start(1000)

    # ── Internal helpers ─────────────────────────────────────────────────

    def _lines(self, request: str) -> list[str]:
        """Send a command and return non-empty response lines without the EOF sentinel."""
        assert self._server is not None
        raw = self._server.process(request)
        lines = [l.rstrip('\r') for l in raw.split('\n')]
        lines = [l for l in lines if l]
        if lines and lines[-1] == 'EOF':
            lines.pop()
        return lines

    def _line(self, request: str) -> str:
        """Send a command and return the single response line."""
        lines = self._lines(request)
        return lines[0] if lines else ''

    # ── Protocol commands ────────────────────────────────────────────────

    def getVersion(self) -> str:
        lines = self._lines("SHOW VERSION")
        self.version = "\n".join(lines)
        return self.version

    def setSettings(self, setting_name: str, setting_value: str) -> str | None:
        translated = {
            "ARMSimUseLabels": "USELABELS",
            "ARMGccCommand": "COMPILER",
            "ARMGccOptions": "ARGS",
            "PATH": "PATH",
        }[setting_name]
        line = self._line("CONFIG {} {}".format(translated, setting_value))
        if line != "OK":
            return (
                "\n".join([
                    "Error when trying to configure the '{}' setting on ARMSim.",
                    "Error message was '{}'.",
                ]).rstrip().format(setting_name, line)
            )
        self._settings[setting_name] = setting_value
        return None

    def _parseRegister(self, line: str) -> tuple[int, str]:
        m = self.re_regexpr.search(line)
        if m is None:
            print("ERROR: Could not parse register from '{}'!".format(line))
            raise ValueError("Could not parse register from '{}'".format(line))
        (reg, hex_value) = m.groups()
        return int(reg), hex_value

    def getRegisters(self) -> list[tuple[int, str]]:
        if not self.connected:
            return []
        lines = self._lines("DUMP REGISTERS")
        return [self._parseRegister(l) for l in lines]

    def getRegister(self, register_name: str) -> tuple[int, str]:
        line = self._line("SHOW REGISTER {}".format(register_name.lower()))
        return self._parseRegister(line)

    def setRegister(self, reg_name: str, hex_value: str) -> str | None:
        line = self._line("SET REGISTER {} WITH {}".format(reg_name, hex_value))
        if line != "OK":
            return "Error when trying to set the register '{}' with the value '{}'.\n".format(
                reg_name, hex_value
            )
        return None

    def getMemoryBanks(self) -> list[tuple[str, str, str]]:
        lines = self._lines("SYSINFO MEMORY")
        memoryBanks: list[tuple[str, str, str]] = []
        for line in lines:
            m = self.re_membanksexpr.search(line)
            if m is None:
                print("ERROR: Could not parse memory bank from '{}'".format(line))
                raise ValueError("Could not parse memory bank from '{}'".format(line))
            (memType, hexStart, hexEnd) = m.groups()
            memoryBanks.append((memType, hexStart, hexEnd))
        return memoryBanks

    def _parseMemory(self, line: str) -> tuple[str, str]:
        m = self.re_memexpr.search(line)
        if m is None:
            print("ERROR: Could not parse memory byte from '{}'".format(line))
            raise ValueError("Could not parse memory byte from '{}'".format(line))
        (hex_address, hex_byte) = m.groups()
        return hex_address, hex_byte

    def getMemory(
        self, hex_start: str, nbytes: int
    ) -> Generator[tuple[str, str], None, None]:
        lines = self._lines("DUMP MEMORY {} {}".format(hex_start, nbytes))
        for line in lines:
            yield self._parseMemory(line)

    def setMemory(self, hexAddress: str, hexValue: str) -> str | None:
        if len(hexValue) > 6:
            cmd = "SET MEMORY WORD AT {} WITH {}".format(hexAddress, hexValue)
        elif len(hexValue) > 4:
            cmd = "SET MEMORY HALF AT {} WITH {}".format(hexAddress, hexValue)
        else:
            cmd = "SET MEMORY BYTE AT {} WITH {}".format(hexAddress, hexValue)
        line = self._line(cmd)
        if line != "OK":
            return "Error when trying to set the memory word at '{}' with the value '{}'.\n".format(
                hexAddress, hexValue
            )
        return None

    @staticmethod
    def _prettyPrintLine(line: str) -> str:
        if line.count(";") == 0:
            return line
        (assembly, ln_source_comment) = [x.strip() for x in line.split(";", 1)]
        try:
            (ln, source_comment) = [x.strip() for x in ln_source_comment.split(" ", 1)]
        except ValueError:
            ln = ln_source_comment
            source_comment = ""
        ln = int(ln)
        if source_comment.count("@"):
            (source, comment) = [x.strip() for x in source_comment.split("@", 1)]
            comment = "@ {}".format(comment)
        else:
            source = source_comment
            comment = ""
        if source.count(":"):
            (label, source) = [x.strip() for x in source.split(":", 1)]
            label = "{}:".format(label)
        else:
            label = ""
        return "{:40};{:-4} {:10} {:20} {}".format(assembly, ln, label, source, comment)

    def getDisassemble(
        self, hexStart: str, nInstructions: int
    ) -> Generator[str, None, None]:
        lines = self._lines("DISASSEMBLE {} {}".format(hexStart, nInstructions))
        for line in lines:
            yield self._prettyPrintLine(line)

    def _getExecuteStep(self, ARMSimCommand: str) -> ExecuteResponse:
        lines = self._lines("EXECUTE {}".format(ARMSimCommand))
        response = ExecuteResponse()
        if len(lines) < 2:
            response.result = "ERROR"
            response.errmsg = "Unexpected response from server: {}".format(lines)
            return response
        response.result = lines[0]
        response.assembly_line = lines[1].split(";")[0]
        mode = ""
        errmsgList: list[str] = []
        for line in lines[2:]:
            if line in ("AFFECTED REGISTERS", "AFFECTED MEMORY", "ERROR MESSAGE"):
                mode = line
                continue
            if mode == "AFFECTED REGISTERS":
                response.registers.append(self._parseRegister(line))
            elif mode == "AFFECTED MEMORY":
                response.memory.append(self._parseMemory(line))
            elif mode == "ERROR MESSAGE":
                errmsgList.append(line)
        response.errmsg = "\n".join(errmsgList)
        return response

    def getExecuteStepInto(self) -> ExecuteResponse:
        return self._getExecuteStep("STEP")

    def getExecuteStepOver(self) -> ExecuteResponse:
        response = self._getExecuteStep("SUBROUTINE")
        if response.errmsg.find("No es subrutina") != -1:
            response.result = "SUCCESS"
            response.errmsg = ""
        return response

    def getExecuteAll(self) -> ExecuteResponse:
        return self._getExecuteStep("ALL")

    def setBreakpoint(self, hex_address: str) -> str | None:
        line = self._line("SET BREAKPOINT AT {}".format(hex_address))
        if line != "OK":
            return "Error when trying to set the breakpoint at '{}'.\n".format(hex_address)
        return None

    def clearBreakpoint(self, hex_address: str) -> str | None:
        line = self._line("CLEAR BREAKPOINT AT {}".format(hex_address))
        if line != "OK":
            return "Error when trying to clear the breakpoint at '{}'.\n".format(hex_address)
        return None

    def clearBreakpoints(self) -> str | None:
        line = self._line("CLEAR BREAKPOINTS")
        if line != "OK":
            return "Error when trying to clear all the breakpoints.\n"
        return None

    # ── Assembly ─────────────────────────────────────────────────────────

    def _copyToTmpDir(self, src_fname: str) -> str:
        tmp_dir = tempfile.mkdtemp(".qtarmsim")
        if self.verbose:
            print("Creating temporary directory: {}".format(tmp_dir))
        dst_fname = "program.s" if src_fname[-2:] != ".c" else "program.c"
        dst_fname = os.path.join(tmp_dir, dst_fname)
        encoding = "utf-8"
        for enc in ["utf-8", "latin1", "ascii"]:
            try:
                with open(src_fname, encoding=enc) as f:
                    _ = f.read()
                encoding = enc
                break
            except UnicodeDecodeError as e:
                if enc == "ascii":
                    raise e
        with open(src_fname, encoding=encoding) as f, open(dst_fname, "w") as dest:
            for line in f:
                _ = dest.write(line)
        return dst_fname

    def _disposeTmpDir(self, fname: str) -> None:
        tmp_dir = os.path.dirname(fname)
        if len(tmp_dir) < 5:
            if self.verbose:
                print(
                    "Cowardly refusing to remove directory '{}' (less than 5 characters).".format(
                        tmp_dir
                    )
                )
            return
        if self.verbose:
            print("Deleting temporary directory '{}'.".format(tmp_dir))
        for f in glob(os.path.join(tmp_dir, "program.*")):
            os.remove(f)
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass

    def doAssemble(self, fname: str) -> AssembleResponse:
        response = AssembleResponse()
        tmp_fname = self._copyToTmpDir(fname)
        # If the input is a C file, compile it to assembly first
        if tmp_fname[-2:] == ".c":
            gcc_command = shlex.split(
                self._settings["ARMGccCommand"]
                + " -S "
                + self._settings["ARMGccOptions"]
                + " "
                + tmp_fname
            )
            process = subprocess.run(
                gcc_command,
                cwd=os.path.dirname(tmp_fname),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            if process.returncode != 0:
                response.result = "ERROR"
                response.errmsg = process.stderr
                self._disposeTmpDir(tmp_fname)
                return response
            tmp_fname = tmp_fname[:-2] + ".s"
        errmsg = self.setSettings(
            "PATH", os.path.dirname(os.path.abspath(tmp_fname)) + "/"
        )
        if errmsg:
            response.result = "ERROR"
            response.errmsg = errmsg
            self._disposeTmpDir(tmp_fname)
            return response
        all_lines = self._lines("ASSEMBLE {}".format(os.path.basename(tmp_fname)))
        response.result = all_lines[0] if all_lines else "ERROR"
        if response.result == "ERROR":
            response.errmsg = "\n".join(all_lines[1:])
        self._disposeTmpDir(tmp_fname)
        return response

    def sendCommand(self, line: str) -> None:
        if self._server is not None:
            self._server.process(line)
