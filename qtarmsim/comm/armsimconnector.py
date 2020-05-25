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

import os
import re
import shlex
import socket
import subprocess
import sys
import tempfile
import time
from glob import glob
from queue import Queue, Empty
from threading import Thread

from PySide2 import QtWidgets, QtCore

from .exceptions import RunTimeOut
from .mysocket import MySocket
from .responses import ExecuteResponse, AssembleResponse


def enqueue_pipe(pipe, queue):
    """
    Reads lines from a pipe and puts them in a queue.

    :param pipe: The pipe from which the lines are to be read.
    :param queue:  The queue where the lines are to be written to.
    """
    for line_bytes in iter(pipe.readline, b''):
        queue.put(line_bytes)
    pipe.close()


def enqueue_file(file, queue):
    """
    Reads lines from a file and puts them in a queue.

    :param file: The file from which the lines are to be read.
    :param queue:  The queue where the lines are to be written to.
    """
    while True:
        line_bytes = file.readline()
        if line_bytes == b'':
            time.sleep(0.5)
            continue
        queue.put(line_bytes)


class ARMSimConnector(QtCore.QObject):
    # Regular expressions as static properties (computed once)
    re_regexpr = re.compile("r([0-9]+): (0[xX][0-9a-fA-F]+)")
    re_membanksexpr = re.compile("([^.:]+).*(0[xX][0-9A-Fa-f]*).*-.*(0[xX][0-9A-Fa-f]*)")
    re_memexpr = re.compile("(0[xX][0-9a-fA-F]+): (0[xX][0-9a-fA-F]+)")

    # Signals
    # noinspection PyUnresolvedReferences
    stdoutLine = QtCore.Signal('QString')

    def __init__(self, verbose=False):
        super().__init__()
        # Set properties default values
        self.verbose = verbose
        self.my_socket = MySocket(verbose=verbose)
        self.armsim_process = None
        # self.setConnected(False, None)
        self._connected = False
        self._current_port = None
        self.version = None
        self.messages = []
        # Create a temporary file where the armsim stdout is redirected to
        tmp_file, tmp_file_name = tempfile.mkstemp(".qtarmsim")
        os.close(tmp_file)
        self.armsim_stdout_write = open(tmp_file_name, 'wb')
        self.armsim_stdout_read = open(tmp_file_name, 'rb')
        # Start a thread that will copy the lines from armsim stdout file to a queue
        self.armsim_stdout_queue = Queue()
        queue_thread = Thread(target=enqueue_file,
                              args=(self.armsim_stdout_read, self.armsim_stdout_queue))
        queue_thread.daemon = True  # thread dies with the program
        queue_thread.start()
        # Initialize and start updateTimer
        self._updateTimer = QtCore.QTimer()
        self._updateTimer.timeout.connect(self.doUpdate)
        self._updateTimer.start(1000)

    def __del__(self):
        """
        On delete, close the opened files and delete them
        """
        self.armsim_stdout_write.close()
        self.armsim_stdout_read.close()
        if os.path.exists(self.armsim_stdout_read.name):
            os.unlink(self.armsim_stdout_read.name)

    def setConnected(self, connected, port=None):
        """
        Sets properties related to the connected status:
          + self.connected
          + self.current_port
          + self.armsim_stdout_queue
        """
        if connected:
            self._connected = True
            self._current_port = port
        else:
            self._connected = False
            self._current_port = None

    @property
    def connected(self):
        return self._connected

    @property
    def current_port(self):
        return self._current_port

    def connect_to(self, command, working_directory, server, port):
        """
        Connects with ARMSim.

        @return: errmsg    An error msg with every connection error (\n as separator), None otherwise
        """

        # =======================================================================
        # Option A) server is a remote server
        # =======================================================================
        if server != "localhost" and server != "127.0.0.1":
            # Try to connect to the given server and port
            self.messages.append("\nTrying to connect to remote ARMSim on port {}...".format(port))
            if self.doConnect(server, port):
                return None
            else:
                return "Could not connect to remote ARMSim server at {}:{}".format(server, port)

        # =======================================================================
        # Option B) server is localhost
        # =======================================================================
        # If and only if self.current_port is set, try to connect to the given server and self.current_port
        if self.current_port:
            self.messages.append("\nTrying to connect to running ARMSim on port {}...".format(self.current_port))
            if self.doConnect(server, self.current_port):
                return None
        # Search for a free port
        free_port = 0
        rest_of_ports = list(range(port + 1, port + 20))
        tmp_socket = MySocket()
        for current_port in [port, ] + rest_of_ports:
            self.messages.append("\nTesting if port {} is free...".format(current_port))
            if tmp_socket.test_port_is_free(current_port):
                self.messages.append("Port {} is available.".format(current_port))
                free_port = current_port
                break
            else:
                self.messages.append("Port {} is already being used.".format(current_port))
        if free_port == 0:
            return "Could not find any port available in the range {}..{}\n\n" \
                   "Please, change the port setting on the preferences dialog.\n".format(port, rest_of_ports[-1])
        # Try to run armsim on the found free_port
        # noinspection PyUnboundLocalVariable
        cmd = shlex.split(command) + [str(current_port), ]
        ON_POSIX = 'posix' in sys.builtin_module_names
        self.messages.append("\nLaunching '{}'...".format(" ".join(cmd)))
        try:
            self.armsim_process = subprocess.Popen(cmd,
                                                   cwd=working_directory,
                                                   stdin=subprocess.DEVNULL,
                                                   stdout=self.armsim_stdout_write,
                                                   stderr=subprocess.PIPE,
                                                   close_fds=ON_POSIX,
                                                   bufsize=1,  # 1 means line buffered
                                                   )
        except OSError as e:
            return "Could not launch the next command:\n" \
                   "    '{}'\n\n" \
                   "On the directory:\n" \
                   "    '{}'\n\n" \
                   "Error was:\n" \
                   "    [Errno {}] {}".format(" ".join(cmd), working_directory, e.errno, e.strerror)
        self.messages.append("Launched")
        # Try to connect to armsim
        self.messages.append("\nConnecting to ARMSim on port {}".format(free_port))
        chances = 0
        while self.armsim_process.poll() is None and not self.doConnect(server, free_port) and chances < 30:
            time.sleep(.1)
            chances += 1
        # Check if self.armsim_process is still alive and we have not consumed all the chances
        if self.armsim_process.poll() is None and chances < 30:
            # Return no error message
            return None
        # Get stderr
        stderr = ""
        try:
            stdout, stderr = self.armsim_process.communicate(timeout=1)  # @UnusedVariable stdout
        except subprocess.TimeoutExpired:
            pass
        # Kill current ARMSim process (if it is still alive)
        if self.armsim_process.poll() is None:
            self.armsim_process.kill()
        # Check stderr and return if not empty
        if stderr:
            return "Could not launch the next command:\n" \
                   "    '{}'\n\n" \
                   "On the directory:\n" \
                   "    '{}'\n\n" \
                   "The error was:\n" \
                   "    {}".format(" ".join(cmd), working_directory, stderr.decode())
        return "Could not bind ARMSim to any port between {} and {}.\n" \
               "\n" \
               "The following messages were reported while trying to establish a connection.\n" \
               "   {}".format(port, rest_of_ports[-1], "\n   ".join(self.messages))

    def doConnect(self, server, port):
        """
        Tries to connect to the given server and port.

        @return: True if successfully connected, False otherwise.
        """
        # 1) Try to connect to the given port
        try:
            self.my_socket.connect_to(port, server=server)
        except ConnectionRefusedError as e:
            self.messages.append("ConnectionRefusedError: ({}) {}.".format(e.errno, e.strerror))
            self.my_socket.close_socket()
            return False
        except OSError as e:
            self.messages.append("OSError: ({}) {}.".format(e.errno, e.strerror))
            self.my_socket.close_socket()
            return False
        # 2) Try to get ARMSim version
        self.my_socket.socket.settimeout(2)  # Set getVersion timeout to 2 seconds
        try:
            self.getVersion()
        except socket.timeout:
            self.messages.append("Timeout occurred.")
            self.my_socket.close_socket()
            return False
        except InterruptedError as e:
            self.messages.append("InterruptedError: ({}) {}.".format(e.errno, e.strerror))
            self.my_socket.close_socket()
            return False
        # Set timeout to something bigger for normal operations
        self.my_socket.socket.settimeout(5.0)
        self.setConnected(True, port)
        return True

    def disconnect_from(self):
        """
        Ends the simulator connection.
        """
        self._sendExit()
        time.sleep(0.5)
        self.my_socket.close_connection()
        self.my_socket.close_socket()
        # Kill current ARMSim process (if it is still alive)
        if self.armsim_process and self.armsim_process.poll() is None:
            self.armsim_process.kill()
        self.setConnected(False)

    def doUpdate(self):
        while True:
            # read line without blocking
            try:
                line_bytes = self.armsim_stdout_queue.get_nowait()  # or .get(timeout=.1)
            except Empty:
                break
            else:  # got line
                try:
                    line = line_bytes.decode("utf-8").rstrip()
                except UnicodeDecodeError as err:
                    line = "UnicodeDecodeError in '{}'".format(line_bytes.decode("utf8", "ignore").rstrip())
                self.stdoutLine.emit(line)
        self._updateTimer.start(1000)

    def getVersion(self):
        """
        Gets the ARMSim Version. This method is also used to confirm that we are speaking to ARMSim and not to
        another server.

        @return: The ARMSim Version text.
        """
        self.my_socket.send_line("SHOW VERSION")
        version_lines = self.my_socket.receive_lines_till_eof()
        self.version = "\n".join(version_lines)
        return self.version

    # @todo: add this to the grammar document
    def setSettings(self, setting_name, setting_value):
        """
        Sets configuration options.

        @return: Error message (or None)
        """
        translated_setting_name = {"ARMSimUseLabels": "USELABELS",
                                   "ARMGccCommand": "COMPILER",
                                   "ARMGccOptions": "ARGS",
                                   "PATH": "PATH",
                                   }[setting_name]
        try:
            self.my_socket.send_line("CONFIG {} {}".format(translated_setting_name, setting_value))
        except BrokenPipeError:
            return "Error when trying to configure the '{}' setting on ARMSim.\n" \
                   "The pipe is broken.".format(setting_name)
        line = self.my_socket.receive_line()
        if line != 'OK':
            return "Error when trying to configure the '{}' setting on ARMSim.\n" \
                   "Error message was '{}'.".format(setting_name, line)
        return None

    def _parseRegister(self, line):
        """
        Parses a line with register content information.

        @return: A pair (register number, hexadecimal content).
        """
        try:
            (reg, hex_value) = self.re_regexpr.search(line).groups()
        except AttributeError:
            print("ERROR: Could not parse register from '{}'!".format(line))
            raise
        return int(reg), hex_value

    def getRegisters(self):
        """
        Gets all the registers from ARMSim.

        @return: An array with pairs (register, contents of that register in hexadecimal)
        """
        if not self.connected:
            return []
        self.my_socket.send_line("DUMP REGISTERS")
        registers = []
        for i in range(17):  # @UnusedVariable i
            line = self.my_socket.receive_line()
            registers.append(self._parseRegister(line))
        return registers

    def getRegister(self, register_name):
        """
        Gets the register data of the register with the given name.

        @return: A pair (register number, contents of the register in hexadecimal)
        """
        self.my_socket.send_line("SHOW REGISTER {}".format(register_name.lower()))
        line = self.my_socket.receive_line()
        return self._parseRegister(line)

    def setRegister(self, reg_name, hex_value):
        """
        Sets the register with name reg_name with the given hex_value.
        """
        self.my_socket.send_line("SET REGISTER {} WITH {}".format(reg_name, hex_value))
        line = self.my_socket.receive_line()
        if line != 'OK':
            return "Error when trying to set the register '{}' with the value '{}'.\n".format(reg_name, hex_value)
        return None

    def getMemoryBanks(self):
        """
        Gets the memory banks available at the simulator.

        @return: An array of tuples as (memory type, hexadecimal start address, hexadecimal end address).
        """
        self.my_socket.send_line("SYSINFO MEMORY")
        lines = self.my_socket.receive_lines_till_eof()
        memory_banks = []
        for line in lines:
            try:
                (memtype, hex_start, hex_end) = self.re_membanksexpr.search(line).groups()
            except AttributeError:
                print("ERROR: Could not parse memory bank from '{}'".format(line))
                raise
            memory_banks.append((memtype, hex_start, hex_end))
        return memory_banks

    def _parseMemory(self, line):
        """
        Parses a line with memory content information.

        @return: A pair (hexadecimal address, hexadecimal byte content)
        """
        try:
            (hex_address, hex_byte) = self.re_memexpr.search(line).groups()
        except AttributeError:
            print("ERROR: Could not parse memory byte from '{}'".format(line))
            raise
        return hex_address, hex_byte

    def getMemory(self, hex_start, nbytes):
        """
        Gets nbytes at most from memory starting at hex_start.

        @return: An array of pairs of the form (hexadecimal memory address, hexadecimal byte).
        """
        self.my_socket.send_line("DUMP MEMORY {} {}".format(hex_start, nbytes))
        for line in self.my_socket.receive_lines_till_eof():
            yield self._parseMemory(line)

    def setMemory(self, hex_address, hex_value):
        """
        Sets the memory at the given hex_address with the given hex_value.
        """
        if len(hex_value) > 6:
            self.my_socket.send_line("SET MEMORY WORD AT {} WITH {}".format(hex_address, hex_value))
        elif len(hex_value) > 4:
            self.my_socket.send_line("SET MEMORY HALF AT {} WITH {}".format(hex_address, hex_value))
        else:
            self.my_socket.send_line("SET MEMORY BYTE AT {} WITH {}".format(hex_address, hex_value))
        line = self.my_socket.receive_line()
        if line != 'OK':
            return "Error when trying to set the memory word at '{}' with the value '{}'.\n".format(hex_address,
                                                                                                    hex_value)
        return None

    @staticmethod
    def _prettyPrintLine(line):
        if line.count(';') == 0:
            return line
        else:
            (assembly, ln_source_comment) = [x.strip() for x in line.split(";", 1)]
            try:
                (ln, source_comment) = [x.strip() for x in ln_source_comment.split(" ", 1)]
            except ValueError:
                ln = ln_source_comment
                source_comment = ''
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

    def getDisassemble(self, hex_start, ninsts):
        """
        Gets the disassemble of ninsts instructions at most starting at hex_start memory address.

        @return: An array of lines with a disassembled instruction in each.
        """
        self.my_socket.send_line("DISASSEMBLE {} {}".format(hex_start, ninsts))
        for line in self.my_socket.receive_lines_till_eof():
            yield self._prettyPrintLine(line)

    def _getExecuteStep(self, ARMSim_command):
        """
        Gets the execute step response.

        @return: An ExecuteResponse object.
        """
        self.my_socket.send_line("EXECUTE {}".format(ARMSim_command))
        lines = [line for line in self.my_socket.receive_lines_till_eof()]
        response = ExecuteResponse()
        response.result = lines[0]
        response.assembly_line = lines[1].split(";")[0]  # get rid of source code part
        mode = ""
        errmsg_list = []
        for line in lines[2:]:
            if line in ("AFFECTED REGISTERS",
                        "AFFECTED MEMORY",
                        "ERROR MESSAGE"):
                mode = line
                continue
            if mode == "AFFECTED REGISTERS":
                response.registers.append(self._parseRegister(line))
            elif mode == "AFFECTED MEMORY":
                response.memory.append(self._parseMemory(line))
            elif mode == "ERROR MESSAGE":
                errmsg_list.append(line)
        response.errmsg = "\n".join(errmsg_list)
        return response

    def getExecuteStepInto(self):
        return self._getExecuteStep("STEP")

    def getExecuteStepOver(self):
        response = self._getExecuteStep("SUBROUTINE")
        # Ignore errors due to the instruction not being a subroutine
        if response.errmsg.find('No es subrutina') != -1:
            response.result = 'SUCCESS'
            response.errmsg = ''
        return response

    def getExecuteAll(self):
        try:
            response = self._getExecuteStep("ALL")
        except socket.timeout:
            raise RunTimeOut()
        return response

    def setBreakpoint(self, hex_address):
        self.my_socket.send_line("SET BREAKPOINT AT {}".format(hex_address))
        line = self.my_socket.receive_line()
        if line != 'OK':
            return "Error when trying to set the breakpoint at '{}'.\n".format(hex_address)
        return None

    def clearBreakpoint(self, hex_address):
        self.my_socket.send_line("CLEAR BREAKPOINT AT {}".format(hex_address))
        line = self.my_socket.receive_line()
        if line != 'OK':
            return "Error when trying to clear the breakpoint at '{}'.\n".format(hex_address)
        return None

    def clearBreakpoints(self):
        self.my_socket.send_line("CLEAR BREAKPOINTS")
        line = self.my_socket.receive_line()
        if line != 'OK':
            return "Error when trying to clear all the breakpoints.\n"
        return None

    def _sendExit(self):
        """
        Sends exit command.
        """
        self.my_socket.send_line("EXIT")

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

    def _copyToTmpDir(self, src_fname):
        """
        Copies the given file to a temporary directory. Returns the name of the new file.
        """
        tmp_dir = tempfile.mkdtemp(".qtarmsim")
        if self.verbose:
            print("Creating temporary directory: {}".format(tmp_dir))
        dst_fname = "program.s" if src_fname[-2:] != '.c' else "program.c"
        dst_fname = os.path.join(tmp_dir, dst_fname)
        # Find the coding of the  original file
        encodings = ['utf-8', 'latin1', 'ascii']
        for i in range(len(encodings)):
            f = open(src_fname, encoding=encodings[i])
            try:
                f.read()
                f.close()
                break
            except UnicodeDecodeError as e:
                f.close()
                if i == len(encodings) - 1:
                    raise e
        # Open the file with the correct encoding
        # noinspection PyUnboundLocalVariable
        f = open(src_fname, encoding=encodings[i])
        dest = open(dst_fname, 'w')
        for line in f:
            dest.write(line)
        f.close()
        dest.close()
        return dst_fname

    def _disposeTmpDir(self, fname):
        """
        Removes the directory where the given file name is.
        """
        tmp_dir = os.path.dirname(fname)
        if len(tmp_dir) < 5:
            if self.verbose:
                print("Cowardly refusing to remove directory '{}' (less than 5 characters).".format(tmp_dir))
            return
        if self.verbose:
            print("Deleting temporary directory '{}'.".format(tmp_dir))
        for fname in glob(os.path.join(tmp_dir, "program.*")):
            os.remove(fname)
        try:
            os.rmdir(tmp_dir)
        except OSError:
            # Directory was not empty (don't raise an exception just for that ;-) )
            pass

    # @todo: add this to the grammar document
    def doAssemble(self, fname):
        response = AssembleResponse()
        tmp_fname = self._copyToTmpDir(fname)
        errmsg = self.setSettings("PATH", os.path.dirname(os.path.abspath(tmp_fname)) + '/')
        if errmsg:
            response.result = "ERROR"
            response.errmsg = errmsg
            self._disposeTmpDir(tmp_fname)
            return response
        self.my_socket.send_line("ASSEMBLE {}".format(os.path.basename(tmp_fname)))
        line = self.my_socket.receive_line()
        response.result = line
        if response.result == "ERROR":
            errmsg_list = self.my_socket.receive_lines_till_eof()
            response.errmsg = "\n".join(errmsg_list)
        self._disposeTmpDir(tmp_fname)
        return response

    def sendCommand(self, line):
        self.my_socket.send_line(line)
        self.my_socket.receive_line()
        QtWidgets.QApplication.processEvents()
        self.my_socket.socket.settimeout(1)  # Set timeout of next lines to 1 second
        while 1:
            try:
                self.my_socket.receive_line()
            except socket.timeout:
                break
            QtWidgets.QApplication.processEvents()
        self.my_socket.socket.settimeout(5)  # Restore default timeout of 5 seconds
