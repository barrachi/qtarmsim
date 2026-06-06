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

# References:
#
# Standard pipe for stdout hangs ARMSim on Windows:
# https://thraxil.org/users/anders/posts/2008/03/13/Subprocess-Hanging-PIPE-is-your-enemy/
#

from __future__ import annotations

import os
import re
import shlex
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Generator
from glob import glob
from io import BufferedReader, BufferedWriter, FileIO
from queue import Empty, Queue
from threading import Thread

from PySide6 import QtWidgets, QtCore

from .exceptions import RunTimeOut
from .mysocket import MySocket
from .responses import ExecuteResponse, AssembleResponse


def enqueue_file(file: FileIO, queue: Queue[bytes]) -> None:
    """
    Reads lines from a file and puts them in a queue.

    :param file: The file from which the lines are to be read.
    :param queue:  The queue where the lines are to be written to.
    """
    while True:
        line_bytes = file.readline()
        if line_bytes == b"":
            time.sleep(0.5)
            continue
        queue.put(line_bytes)


class ARMSimConnector(QtCore.QObject):
    # Regular expressions as static properties (computed once)
    re_regexpr: re.Pattern[str] = re.compile("r([0-9]+): (0[xX][0-9a-fA-F]+)")
    re_membanksexpr: re.Pattern[str] = re.compile(
        "([^.:]+).*(0[xX][0-9A-Fa-f]*).*-.*(0[xX][0-9A-Fa-f]*)"
    )
    re_memexpr: re.Pattern[str] = re.compile("(0[xX][0-9a-fA-F]+): (0[xX][0-9a-fA-F]+)")

    # Signals
    stdoutLine: QtCore.Signal = QtCore.Signal(str)

    def __init__(self, verbose: bool = False) -> None:
        super().__init__()
        # Set properties default values
        self.verbose: bool = verbose
        self.mySocket: MySocket = MySocket(verbose=verbose)
        self.armsimProcess: subprocess.Popen[bytes] | None = None
        # self.setConnected(False, None)
        self._connected: bool = False
        self._currentPort: int | None = None
        self.version: str
        self.messages: list[str] = []
        # Create a temporary file where the armsim stdout is redirected to
        tmp_file, tmp_file_name = tempfile.mkstemp(".qtarmsim")
        os.close(tmp_file)
        self.armsimStdoutWrite: BufferedWriter = open(tmp_file_name, "wb")
        self.armsimStdoutRead: BufferedReader = open(tmp_file_name, "rb")
        # Start a thread that will copy the lines from the armsim stdout file to a queue
        self.armsimStdoutQueue: Queue[bytes] = Queue()
        queue_thread = Thread(
            target=enqueue_file,
            args=(self.armsimStdoutRead, self.armsimStdoutQueue),
        )
        queue_thread.daemon = True  # thread dies with the program
        queue_thread.start()
        # Initialize and start updateTimer
        self._updateTimer: QtCore.QTimer = QtCore.QTimer()
        _ = self._updateTimer.timeout.connect(self.doUpdate)
        self._updateTimer.start(1000)
        # Settings for invoking gcc
        self._settings: dict[str, str] = {}

    def __del__(self) -> None:
        """
        On delete, close the opened files and delete them
        """
        self.armsimStdoutWrite.close()
        self.armsimStdoutRead.close()
        if os.path.exists(self.armsimStdoutRead.name):
            os.unlink(self.armsimStdoutRead.name)

    def setConnected(self, connected: bool, port: int | None = None) -> None:
        """
        Sets properties related to the connected status:
          + self.connected
          + self.current_port
          + self.armsim_stdout_queue
        """
        if connected:
            self._connected = True
            self._currentPort = port
        else:
            self._connected = False
            self._currentPort = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def currentPort(self) -> int | None:
        return self._currentPort

    def connectTo(
        self, command: str, working_directory: str, server: str, port: int
    ) -> str | None:
        """
        Connects with ARMSim.

        @return: errmsg    An error msg with every connection error (\n as separator), None otherwise
        """

        # =======================================================================
        # Option A) server is a remote server
        # =======================================================================
        if server != "localhost" and server != "127.0.0.1":
            # Try to connect to the given server and port
            self.messages.append(
                "\nTrying to connect to remote ARMSim on port {}...".format(port)
            )
            if self.doConnect(server, port):
                return None
            else:
                return "Could not connect to remote ARMSim server at {}:{}".format(
                    server, port
                )

        # =======================================================================
        # Option B) server is localhost
        # =======================================================================
        # If and only if self.current_port is set, try to connect to the given server and self.current_port
        if self.currentPort:
            self.messages.append(
                "\nTrying to connect to running ARMSim on port {}...".format(
                    self.currentPort
                )
            )
            if self.doConnect(server, self.currentPort):
                return None
        # Search for a free port
        free_port = 0
        rest_of_ports: list[int] = list(range(port + 1, port + 20))
        tmp_socket = MySocket(register_sigint=False)
        for current_port in [
            port,
        ] + rest_of_ports:
            self.messages.append("\nTesting if port {} is free...".format(current_port))
            if tmp_socket.testPortIsFree(current_port):
                self.messages.append("Port {} is available.".format(current_port))
                free_port = current_port
                break
            else:
                self.messages.append(
                    "Port {} is already being used.".format(current_port)
                )
        if free_port == 0:
            return (
                "Could not find any port available in the range {}..{}\n\n".format(
                    port, rest_of_ports[-1]
                )
                + "Please, change the port setting on the preferences dialog.\n"
            )
        # Try to run armsim on the found free_port
        # noinspection PyUnboundLocalVariable
        cmd = shlex.split(command) + [str(free_port)]
        ON_POSIX = "posix" in sys.builtin_module_names
        self.messages.append("\nLaunching '{}'...".format(" ".join(cmd)))
        try:
            self.armsimProcess = subprocess.Popen(
                cmd,
                cwd=working_directory,
                stdin=subprocess.DEVNULL,
                stdout=self.armsimStdoutWrite,
                stderr=subprocess.PIPE,
                close_fds=ON_POSIX,
            )
        except OSError as e:
            return (
                "\n".join([
                    "Could not launch the next command:",
                    "    '{}'\n",
                    "On the directory:",
                    "    '{}'\n",
                    "Error was:",
                    "    [Errno {}] {}",
                ]).rstrip().format(" ".join(cmd), working_directory, e.errno, e.strerror)
            )
        self.messages.append("Launched")
        # Wait for the server to announce the port it actually bound to.
        # The server may have moved to the next free port on its own.
        for _ in range(50):  # up to 5 seconds
            try:
                line_bytes = self.armsimStdoutQueue.get(timeout=0.1)
                line_str = line_bytes.decode("utf-8", errors="replace").strip()
                self.messages.append(line_str)
                m = re.search(r"listening on port (\d+)", line_str)
                if m:
                    free_port = int(m.group(1))
                    self.messages.append("Server bound to port {}.".format(free_port))
                    break
            except Empty:
                if self.armsimProcess.poll() is not None:
                    break
        # Try to connect to armsim
        self.messages.append("\nConnecting to ARMSim on port {}".format(free_port))
        chances = 0
        while (
            self.armsimProcess.poll() is None
            and not self.doConnect(server, free_port)
            and chances < 30
        ):
            time.sleep(0.1)
            chances += 1
        # Check if self.armsim_process is still alive, and we have not consumed all the chances
        if self.armsimProcess.poll() is None and chances < 30:
            # Return no error message
            return None
        # Get stderr
        stderr = ""
        try:
            _, stderr = self.armsimProcess.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            pass
        # Kill current ARMSim process (if it is still alive)
        if self.armsimProcess.poll() is None:
            self.armsimProcess.kill()
        # Check stderr and return if not empty
        if stderr:
            return (
                "\n".join([
                    "Could not launch the next command:",
                    "    '{}'\n",
                    "On the directory:",
                    "    '{}'\n",
                    "The error was:",
                    "    {}"
                    ]).rstrip().format(" ".join(cmd), working_directory, stderr.decode())
            )
        return (
            "\n".join([
                "Could not bind ARMSim to any port between {} and {}.",
                "",
                "The following messages were reported while trying to establish a connection.",
                "   {}"
            ]).rstrip().format(port, rest_of_ports[-1], "\n   ".join(self.messages))
        )

    def doConnect(self, server: str, port: int) -> bool:
        """
        Tries to connect to the given server and port.

        @return: True if successfully connected, False otherwise.
        """
        # 1) Try to connect to the given port
        try:
            self.mySocket.connectTo(port, server=server)
        except ConnectionRefusedError as e:
            self.messages.append(
                "ConnectionRefusedError: ({}) {}.".format(e.errno, e.strerror)
            )
            self.mySocket.closeConnection()
            return False
        except OSError as e:
            self.messages.append("OSError: ({}) {}.".format(e.errno, e.strerror))
            self.mySocket.closeConnection()
            return False
        # 2) Try to get ARMSim version
        assert self.mySocket.conn is not None
        self.mySocket.conn.settimeout(2)  # Set getVersion timeout to 2 seconds
        try:
            _ = self.getVersion()
        except socket.timeout:
            self.messages.append("Timeout occurred.")
            self.mySocket.closeConnection()
            return False
        except InterruptedError as e:
            self.messages.append(
                "InterruptedError: ({}) {}.".format(e.errno, e.strerror)
            )
            self.mySocket.closeConnection()
            return False
        # Set timeout to something bigger for normal operations
        self.mySocket.conn.settimeout(5.0)
        self.setConnected(True, port)
        return True

    def disconnect_from(self) -> None:
        """
        Ends the simulator connection.
        """
        self._sendExit()
        time.sleep(0.5)
        self.mySocket.closeConnection()
        # Kill the current ARMSim process (if it is still alive)
        if self.armsimProcess and self.armsimProcess.poll() is None:
            self.armsimProcess.kill()
        self.setConnected(False)

    def doUpdate(self) -> None:
        while True:
            # read line without blocking
            try:
                line_bytes = self.armsimStdoutQueue.get_nowait()  # or .get(timeout=.1)
            except Empty:
                break
            else:  # got line
                try:
                    line = line_bytes.decode("utf-8").rstrip()
                except UnicodeDecodeError:
                    line = "UnicodeDecodeError in '{}'".format(
                        line_bytes.decode("utf8", "ignore").rstrip()
                    )
                self.stdoutLine.emit(line)
        self._updateTimer.start(1000)

    def getVersion(self) -> str:
        """
        Gets the ARMSim Version. This method is also used to confirm that we are speaking to ARMSim and not to
        another server.

        @return: The ARMSim Version text.
        """
        self.mySocket.sendLine("SHOW VERSION")
        version_lines = self.mySocket.receiveLinesTillEof()
        self.version = "\n".join(version_lines)
        return self.version

    # @todo: add this to the grammar document
    def setSettings(self, setting_name: str, setting_value: str) -> str | None:
        """
        Sets configuration options.

        @return: Error message (or None)
        """
        translated_setting_name = {
            "ARMSimUseLabels": "USELABELS",
            "ARMGccCommand": "COMPILER",
            "ARMGccOptions": "ARGS",
            "PATH": "PATH",
        }[setting_name]
        try:
            self.mySocket.sendLine(
                "CONFIG {} {}".format(translated_setting_name, setting_value)
            )
        except BrokenPipeError:
            return (
                "\n".join([
                    "Error when trying to configure the '{}' setting on ARMSim.",
                    "The pipe is broken."
                ]).rstrip().format(setting_name)
            )
        line = self.mySocket.receiveLine()
        if line != "OK":
            return (
                "\n".join([
                    "Error when trying to configure the '{}' setting on ARMSim.",
                    "Error message was '{}'."
                ]).rstrip().format(setting_name, line)
            )
        self._settings[setting_name] = setting_value
        return None

    def _parseRegister(self, line: str) -> tuple[int, str]:
        """
        Parses a line with register content information.

        @return: A pair (register number, hexadecimal content).
        """
        m = self.re_regexpr.search(line)
        if m is None:
            print("ERROR: Could not parse register from '{}'!".format(line))
            raise ValueError("Could not parse register from '{}'".format(line))
        (reg, hex_value) = m.groups()
        return int(reg), hex_value

    def getRegisters(self) -> list[tuple[int, str]]:
        """
        Gets all the registers from ARMSim.

        @return: An array with pairs (register, contents of that register in hexadecimal)
        """
        if not self.connected:
            return []
        self.mySocket.sendLine("DUMP REGISTERS")
        registers: list[tuple[int, str]] = []
        for _ in range(17):
            line = self.mySocket.receiveLine()
            registers.append(self._parseRegister(line))
        return registers

    def getRegister(self, register_name: str) -> tuple[int, str]:
        """
        Gets the register data of the register with the given name.

        @return: A pair (register number, contents of the register in hexadecimal)
        """
        self.mySocket.sendLine("SHOW REGISTER {}".format(register_name.lower()))
        line = self.mySocket.receiveLine()
        return self._parseRegister(line)

    def setRegister(self, reg_name: str, hex_value: str) -> str | None:
        """
        Sets the register with name reg_name with the given hex_value.
        """
        self.mySocket.sendLine("SET REGISTER {} WITH {}".format(reg_name, hex_value))
        line = self.mySocket.receiveLine()
        if line != "OK":
            return "Error when trying to set the register '{}' with the value '{}'.\n".format(
                reg_name, hex_value
            )
        return None

    def getMemoryBanks(self) -> list[tuple[str, str, str]]:
        """
        Gets the memory banks available at the simulator.

        @return: An array of tuples as (memory type, hexadecimal start address, hexadecimal end address).
        """
        self.mySocket.sendLine("SYSINFO MEMORY")
        lines = self.mySocket.receiveLinesTillEof()
        memoryBanks: list[tuple[str, str, str]] = []
        for line in lines:
            m: re.Match[str] | None = self.re_membanksexpr.search(line)
            if m is None:
                print("ERROR: Could not parse memory bank from '{}'".format(line))
                raise ValueError("Could not parse memory bank from '{}'".format(line))
            (memType, hexStart, hexEnd) = m.groups()
            memoryBanks.append((memType, hexStart, hexEnd))
        return memoryBanks

    def _parseMemory(self, line: str) -> tuple[str, str]:
        """
        Parses a line with memory content information.

        @return: A pair (hexadecimal address, hexadecimal byte content)
        """
        m = self.re_memexpr.search(line)
        if m is None:
            print("ERROR: Could not parse memory byte from '{}'".format(line))
            raise ValueError("Could not parse memory byte from '{}'".format(line))
        (hex_address, hex_byte) = m.groups()
        return hex_address, hex_byte

    def getMemory(
        self, hex_start: str, nbytes: int
    ) -> Generator[tuple[str, str], None, None]:
        """
        Gets nbytes at most from memory starting at hex_start.

        @return: An array of (hexadecimal memory address, hexadecimal byte) pairs.
        """
        self.mySocket.sendLine("DUMP MEMORY {} {}".format(hex_start, nbytes))
        for line in self.mySocket.receiveLinesTillEof():
            yield self._parseMemory(line)

    def setMemory(self, hexAddress: str, hexValue: str) -> str | None:
        """
        Sets the memory at the given hex_address with the given hex_value.
        """
        if len(hexValue) > 6:
            self.mySocket.sendLine(
                "SET MEMORY WORD AT {} WITH {}".format(hexAddress, hexValue)
            )
        elif len(hexValue) > 4:
            self.mySocket.sendLine(
                "SET MEMORY HALF AT {} WITH {}".format(hexAddress, hexValue)
            )
        else:
            self.mySocket.sendLine(
                "SET MEMORY BYTE AT {} WITH {}".format(hexAddress, hexValue)
            )
        line = self.mySocket.receiveLine()
        if line != "OK":
            return "Error when trying to set the memory word at '{}' with the value '{}'.\n".format(
                hexAddress, hexValue
            )
        return None

    @staticmethod
    def _prettyPrintLine(line: str) -> str:
        if line.count(";") == 0:
            return line
        else:
            (assembly, ln_source_comment) = [x.strip() for x in line.split(";", 1)]
            try:
                (ln, source_comment) = [
                    x.strip() for x in ln_source_comment.split(" ", 1)
                ]
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
            return "{:40};{:-4} {:10} {:20} {}".format(
                assembly, ln, label, source, comment
            )

    def getDisassemble(
        self, hexStart: str, nInstructions: int
    ) -> Generator[str, None, None]:
        """
        Gets the disassembly of n instructions at most starting at hex_start memory address.

        @return: An array of lines with a disassembled instruction in each.
        """
        self.mySocket.sendLine("DISASSEMBLE {} {}".format(hexStart, nInstructions))
        for line in self.mySocket.receiveLinesTillEof():
            yield self._prettyPrintLine(line)

    def _getExecuteStep(self, ARMSimCommand: str) -> ExecuteResponse:
        """
        Gets the execute step response.

        @return: An ExecuteResponse object.
        """
        self.mySocket.sendLine("EXECUTE {}".format(ARMSimCommand))
        lines = list(self.mySocket.receiveLinesTillEof())
        response = ExecuteResponse()
        if len(lines) < 2:
            response.result = "ERROR"
            response.errmsg = "Unexpected response from server: {}".format(lines)
            return response
        response.result = lines[0]
        response.assembly_line = lines[1].split(";")[0]  # get rid of the source code part
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
        # Ignore errors due to the instruction not being a subroutine
        if response.errmsg.find("No es subrutina") != -1:
            response.result = "SUCCESS"
            response.errmsg = ""
        return response

    def getExecuteAll(self) -> ExecuteResponse:
        try:
            response = self._getExecuteStep("ALL")
        except socket.timeout:
            raise RunTimeOut()
        return response

    def setBreakpoint(self, hex_address: str) -> str | None:
        self.mySocket.sendLine("SET BREAKPOINT AT {}".format(hex_address))
        line = self.mySocket.receiveLine()
        if line != "OK":
            return "Error when trying to set the breakpoint at '{}'.\n".format(
                hex_address
            )
        return None

    def clearBreakpoint(self, hex_address: str) -> str | None:
        self.mySocket.sendLine("CLEAR BREAKPOINT AT {}".format(hex_address))
        line = self.mySocket.receiveLine()
        if line != "OK":
            return "Error when trying to clear the breakpoint at '{}'.\n".format(
                hex_address
            )
        return None

    def clearBreakpoints(self) -> str | None:
        self.mySocket.sendLine("CLEAR BREAKPOINTS")
        line = self.mySocket.receiveLine()
        if line != "OK":
            return "Error when trying to clear all the breakpoints.\n"
        return None

    def _sendExit(self) -> None:
        """
        Sends exit command.
        """
        self.mySocket.sendLine("EXIT")

    # ===============================================================================
    # ASSEMBLE fich[.s] (vamos, que la extensión es ignorada)
    # devuelve
    # SUCCESS en caso de que haya ido bien
    # ERROR
    # lineas de error
    # devueltas por el
    # compilador
    # EOF
    # En caso de error, todas terminadas en \r\n.
    # ===============================================================================

    def _copyToTmpDir(self, src_fname: str) -> str:
        """
        Copies the given file to a temporary directory. Returns the name of the new file.
        """
        tmp_dir = tempfile.mkdtemp(".qtarmsim")
        if self.verbose:
            print("Creating temporary directory: {}".format(tmp_dir))
        dst_fname = "program.s" if src_fname[-2:] != ".c" else "program.c"
        dst_fname = os.path.join(tmp_dir, dst_fname)
        # Find the coding of the original file
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
        # Copy the file with the detected encoding
        with open(src_fname, encoding=encoding) as f, open(dst_fname, "w") as dest:
            for line in f:
                _ = dest.write(line)
        return dst_fname

    def _disposeTmpDir(self, fname: str) -> None:
        """
        Removes the directory where the given file name is.
        """
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
        for fname in glob(os.path.join(tmp_dir, "program.*")):
            os.remove(fname)
        try:
            os.rmdir(tmp_dir)
        except OSError:
            # The directory was not empty (don't raise an exception just for that ;-))
            pass

    # @todo: add this to the grammar document
    def doAssemble(self, fname: str) -> AssembleResponse:
        response = AssembleResponse()
        tmp_fname = self._copyToTmpDir(fname)
        # If the input is a c file, get its assembly version
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
        # end of c file processing
        errmsg = self.setSettings(
            "PATH", os.path.dirname(os.path.abspath(tmp_fname)) + "/"
        )
        if errmsg:
            response.result = "ERROR"
            response.errmsg = errmsg
            self._disposeTmpDir(tmp_fname)
            return response
        self.mySocket.sendLine("ASSEMBLE {}".format(os.path.basename(tmp_fname)))
        line = self.mySocket.receiveLine()
        response.result = line
        if response.result == "ERROR":
            errmsg_list = self.mySocket.receiveLinesTillEof()
            response.errmsg = "\n".join(errmsg_list)
        self._disposeTmpDir(tmp_fname)
        return response

    def sendCommand(self, line: str) -> None:
        self.mySocket.sendLine(line)
        _ = self.mySocket.receiveLine()
        QtWidgets.QApplication.processEvents()
        conn = self.mySocket.conn
        assert conn is not None
        conn.settimeout(1)  # Set timeout of next lines to 1 second
        while 1:
            try:
                _ = self.mySocket.receiveLine()
            except socket.timeout:
                break
            QtWidgets.QApplication.processEvents()
        conn.settimeout(5)  # Restore default timeout of 5 seconds
