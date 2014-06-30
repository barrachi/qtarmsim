# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of Qt ARMSim.                                        #
#                                                                         #
#  Qt ARMSim is free software: you can redistribute it and/or modify      #
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

import os
import re
import subprocess
import time

from src.mysocket import MySocket
import socket


## Execute response container
class ExecuteResponse():
    
    def __init__(self):
        self.result = ""
        self.assembly_line = ""
        self.registers = []
        self.memory = []
        self.errmsg = []

## Assemble response container
class AssembleResponse():
    
    def __init__(self):
        self.result = ""
        self.errmsg = []


class ARMSimConnector():

    # Regular expressions as static properties (computed once)
    re_regexpr = re.compile("r([0-9]+): (0[xX][0-9a-fA-F]+)")
    re_membanksexpr = re.compile("([^.:]+).*(0[xX][0-9A-Fa-f]*).*-.*(0[xX][0-9A-Fa-f]*)")
    re_memexpr = re.compile("(0[xX][0-9a-fA-F]+): (0[xX][0-9a-fA-F]+)")

    def __init__(self):
        # Set properties default values
        self.mysocket = MySocket()
        self.armsim_pid = None
        self.setConnected(False, None)
        self.version = None
        
    def setConnected(self, connected, port):
        """
        Sets properties related to the connected status:
          * self.connected
          * self.current_port
          * self.code_is_assembled
        """
        if connected:
            self.connected = True
            self.current_port = port
        else:
            self.connected = False
            self.current_port = None
        # If setConnected is called, it forces code_is_assembled to be set to False
        self.code_is_assembled = False
            
        
    def connect(self, command, server, port, minimum_port, maximum_port, gcc_command, gcc_options):
        """
        Connects with ARMSim.
        
        @return: errmsg     An error msg if an error occurred, None otherwise   
        """
        # 1) Search if ARMSim is already listening in a port in the range [port,] + [minimum_port, maximum_port]
        for current_port in [port, ] + list(range(minimum_port, maximum_port+1)):
            try:
                self.mysocket.connect_to(current_port, server=server)
                self.mysocket.sock.settimeout(2.0) # Set timeout to 2 seconds
            except ConnectionRefusedError:
                continue
            try:
                self.getVersion()
            except socket.timeout:
                return "Socket timeout when trying to get ARMSim version"
            self.setConnected(True, current_port)
            return None
        if server != "localhost":
            return "Could not connect to ARMSim server at {}:{}-{}".format(server, minimum_port, maximum_port)
        # 2) Else, if server == "localhost", then launch a new copy of ARMSim 
        self.armsim_pid = subprocess.Popen(["ruby",
                                            command, 
                                            str(port)],
                                            cwd = os.path.dirname(command)
                                           ).pid
        if not self.armsim_pid:
            return "Could not launch ARMSim command '{}'".format(command)
        chances = 3
        while chances:
            try:
                self.mysocket.connect_to(port)
                self.mysocket.sock.settimeout(2.0) # Set timeout to 2 seconds
                break
            except ConnectionRefusedError:
                # Sleep half a second while the server gets ready
                time.sleep(.5)
                chances -= 1
        if chances == 0:
            return "ARMSim refused to open a connection at port {}.".format(port)
        if not self.getVersion():
            return "ARMSim could be listening at port {}, but it does not answer as expected.".format(port)
        
        # 3) Try to set configuration options for localhost execution
        errmsg = self.setConfigOptions(gcc_command, gcc_options)
        if errmsg:
            return errmsg

        # 4) Mark as connected and return no error message
        self.setConnected(True, port)
        return None
    
    
    def disconnect(self):
        """
        Closes the socket. See also sendExit().
        """
        self.mysocket.close_connection()
        self.mysocket.close_socket()
        self.connected = False
        
    def getVersion(self):
        """
        Gets the ARMSim Version. This method is also used to confirm that we are speaking to ARMSim and not to another server.
        
        @return: The ARMSim Version text.
        """
        if self.version:
            return self.version
        else:
            self.mysocket.send_line("SHOW VERSION")
            version_lines = self.mysocket.receive_lines_till_eof()
            self.version = "\n".join(version_lines)
            return self.version
    
    #@todo: add this to the grammar document
    def setConfigOptions(self, gcc_command, gcc_options):
        """
        Sets configuration options.
        
        @return: Error message (or None)
        """
        self.mysocket.send_line("CONFIG COMPILER {}".format(gcc_command))
        line = self.mysocket.receive_line()
        if line != 'OK':
            return "Error when trying to configure the compiler command"
        self.mysocket.send_line("CONFIG ARGS {}".format(gcc_options))
        line = self.mysocket.receive_line()
        if line != 'OK':
            return "Error when trying to configure the compiler options"
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
        return (int(reg), hex_value) 
    
    def getRegisters(self):
        """
        Gets all the registers from ARMSim.
        
        @return: An array with pairs (register, contents of that register in hexadecimal)
        """
        if not self.connected:
            return []
        self.mysocket.send_line("DUMP REGISTERS")
        registers = []
        for i in range(16):  # @UnusedVariable i
            line = self.mysocket.receive_line()
            registers.append(self._parseRegister(line))
        return registers


    def getMemoryBanks(self):
        """
        Gets the memory banks available at the simulator.
        
        @return: An array of tuples as (memory type, hexadecimal start address, hexadecimal end address).
        """
        self.mysocket.send_line("SYSINFO MEMORY")
        lines = self.mysocket.receive_lines_till_eof()

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
        return ((hex_address, hex_byte))
    
    def getMemory(self, hex_start, nbytes):
        """
        Gets nbytes at most from memory starting at hex_start.
        
        @return: An array of pairs of the form (hexadecimal memory address, hexadecimal byte).
        """
        self.mysocket.send_line("DUMP MEMORY {} {}".format(hex_start, nbytes))
        lines = self.mysocket.receive_lines_till_eof()
        memory_bytes = []
        for line in lines:
            memory_bytes.append(self._parseMemory(line))
        return memory_bytes
            

    def getDisassemble(self, hex_start, ninsts):
        """
        Gets the disassemble of ninsts instructions at most starting at hex_start memory address.
        
        @return: An array of lines with a disassembled instruction in each.
        """
        self.mysocket.send_line("DISASSEMBLE {} {}".format(hex_start, ninsts))
        return self.mysocket.receive_lines_till_eof()


    def getExecuteStep(self):
        """
        Gets the execute step response.
        
        @return: An ExecuteResponse object.
        """
        self.mysocket.send_line("EXECUTE STEP")
        lines = self.mysocket.receive_lines_till_eof()
        response = ExecuteResponse()
        response.result = lines[0]
        response.assembly_line = lines[1]
        mode = ""
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
                response.errmsg.append(line)
        return response

    def sendExit(self):
        """
        Sends exit command.
        """
        self.mysocket.send_line("EXIT")
        self.disconnect()
        time.sleep(0.5)


    #@todo: add this to the grammar document
    def _setConfigPath(self, path):
        """
        Sets the current directory path.
        
        @return: Error message (or None)
        """
        self.mysocket.send_line("CONFIG PATH {}".format(path))
        line = self.mysocket.receive_line()
        if line != 'OK':
            return "Error when trying to configure the working directory path"
        return None

#===============================================================================
# ASSEMBLE fich[.s] (vamos, que la extensión es ignorada)
# devuelve
# SUCCESS en caso de que todo vaya bien
# ERROR
# lineas de error
# devueltas por el
# compilador
# EOF
# En caso de error, todas terminadas en \r\n.
#===============================================================================


    #@todo: add this to the grammar document
    def doAssemble(self, path):
        response = AssembleResponse()
        errmsg = self._setConfigPath(os.path.dirname(os.path.abspath(path)))
        if errmsg:
            response.result = "ERROR"
            response.errmsg.append(errmsg)
            return response
        self.mysocket.send_line("ASSEMBLE {}".format(os.path.basename(path)))
        line = self.mysocket.receive_line()
        response.result = line
        if response == "ERROR":
            response.errmsg = self.mysocket.receive_lines_till_eof()
        return response
