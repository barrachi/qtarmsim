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

from .mysocket import MySocket
import socket


## Execute response container
class ExecuteResponse():
    
    def __init__(self):
        self.result = ""
        self.assembly_line = ""
        self.registers = []
        self.memory = []
        self.errmsg = ""

## Assemble response container
class AssembleResponse():
    
    def __init__(self):
        self.result = ""
        self.errmsg = ""


class ARMSimConnector():

    # Regular expressions as static properties (computed once)
    re_regexpr = re.compile("r([0-9]+): (0[xX][0-9a-fA-F]+)")
    re_membanksexpr = re.compile("([^.:]+).*(0[xX][0-9A-Fa-f]*).*-.*(0[xX][0-9A-Fa-f]*)")
    re_memexpr = re.compile("(0[xX][0-9a-fA-F]+): (0[xX][0-9a-fA-F]+)")

    def __init__(self):
        # Set properties default values
        self.mysocket = MySocket()
        self.armsim_process = None
        self.setConnected(False, None)
        self.version = None
        self.messages = []
        
    def setConnected(self, connected, port):
        """
        Sets properties related to the connected status:
          * self.connected
          * self.current_port
        """
        if connected:
            self.connected = True
            self.current_port = port
        else:
            self.connected = False
            self.current_port = None
            
        
    def connect(self, command, server, port, minimum_port, maximum_port):
        """
        Connects with ARMSim.
        
        @return: errmsg    An error msg with every connection error (\n as separator), None otherwise   
        """
        # 1) Try to connect to the given server and port
        self.messages.append("\nTrying to connect to port {} (first attempt)...".format(port))
        if self.doConnect(server, port):
            # Mark as connected and return no error message
            self.setConnected(True, port)
            return None
        else:
            if server != "localhost":
                return "Could not connect to ARMSim server at {}:{}".format(server, port)
            # 1.1) If server == localhost, launch ARMSim on any possible port
            connected = False
            #rest_of_ports = [x for x in range(minimum_port, maximum_port+1) if x != port]
            rest_of_ports = list(range(port+1, port+10))
            for current_port in [port, ] + rest_of_ports:
                self.messages.append("\nTrying to connect to port {}...".format(current_port))
                cmd = ["ruby", os.path.basename(command), str(current_port) ]
                try:
                    self.armsim_process = subprocess.Popen(cmd,
                                                           cwd = os.path.dirname(command),
                                                           stderr = subprocess.PIPE
                                                           )
                except Exception as e:
                    return  "Could not launch the next command:\n" \
                            "    '{}'\n\n" \
                            "on the directory:\n" \
                            "    '{}'\n\n" \
                            "Error was:\n" \
                            "    [Errno {}] {}".format(" ".join(cmd), os.path.dirname(command), e.errno, e.strerror)
                chances = 0
                while self.armsim_process.poll() == None and not self.doConnect(server, current_port) and chances < 3:
                    time.sleep(.5)
                    chances += 1
                # Check if self.armsim_process is still alive and we have not consumed all the chances
                if self.armsim_process.poll() == None and chances < 3:
                    # Mark as connected and return no error message
                    self.setConnected(True, current_port)
                    return None
                else:
                    # Get stderr
                    stderr = ""
                    try:
                        (stdout, stderr) = self.armsim_process.communicate(timeout = 1)  # @UnusedVariable stdout
                    except:
                        pass
                    # Kill current ARMSim process (if it is still alive)
                    if self.armsim_process.poll() == None:
                        self.armsim_process.kill()
                    # Check previously gotten stderr, only return now if it is a ruby error
                    if stderr and stderr.decode().count("ruby"):
                        return  "Could not launch the next command:\n" \
                                "    '{}'\n\n" \
                                "on the directory:\n" \
                                "    '{}'\n\n" \
                                "The error was:\n" \
                                "    {}".format(" ".join(cmd), os.path.dirname(command), stderr.decode())
            if not connected:
                return "Could not bind ARMSim to any port between {} and {}.\n" \
                        "\n" \
                        "The next errors occurred while trying to establish a connection:\n" \
                        "   {}".format(port, rest_of_ports[-1], "\n   ".join(self.messages))


    def doConnect(self, server, port):
        """
        Tries to connect to the given server and port.
        
        @return: True if successfully connected, False otherwise.
        """
        try:
            self.mysocket.connect_to(port, server=server)
            self.mysocket.sock.settimeout(0.2)  # Set timeout to .2 seconds
        except ConnectionRefusedError as e:
            self.messages.append("ConnectionRefusedError: ({}) {}".format(e.errno, e.strerror))
            self.mysocket.close_socket()
            return False
        except OSError as e:
            self.messages.append("OSError: ({}) {}".format(e.errno, e.strerror))
            self.mysocket.close_socket()
            return False
        try:
            self.getVersion()
        except socket.timeout as e:
            self.messages.append("Timeout occurred")
            self.mysocket.close_socket()
            return False
        except InterruptedError as e:
            self.messages.append("InterruptedError: ({}) {}".format(e.errno, e.strerror))
            self.mysocket.close_socket()
            return False
        # Set timeout to something bigger
        self.mysocket.sock.settimeout(4.0)
        return True
    
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
        self.mysocket.send_line("SHOW VERSION")
        version_lines = self.mysocket.receive_lines_till_eof()
        self.version = "\n".join(version_lines) 
        return self.version
    
    #@todo: add this to the grammar document
    def setSettings(self, setting_name, setting_value):
        """
        Sets configuration options.
        
        @return: Error message (or None)
        """
        translated_setting_name = {"ARMGccCommand": "COMPILER",
                                   "ARMGccOptions": "ARGS",
                                   "PATH": "PATH",
                                   }[setting_name]
        self.mysocket.send_line("CONFIG {} {}".format(translated_setting_name, setting_value))
        line = self.mysocket.receive_line()
        if line != 'OK':
            return "Error when trying to configure the '{}' setting on ARMSim".format(setting_name)
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


    def _getExecuteStep(self, ARMSim_command):
        """
        Gets the execute step response.
        
        @return: An ExecuteResponse object.
        """
        self.mysocket.send_line("EXECUTE {}".format(ARMSim_command))
        lines = self.mysocket.receive_lines_till_eof()
        print(lines)
        response = ExecuteResponse()
        response.result = lines[0]
        response.assembly_line = lines[1]
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
        return self._getExecuteStep("SUBROUTINE")
    
    def getExecuteAll(self):
        return self._getExecuteStep("ALL")
        
    def sendExit(self):
        """
        Sends exit command.
        """
        self.mysocket.send_line("EXIT")
        self.disconnect()
        time.sleep(0.5)



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
        self.has_assembled_code = False
        response = AssembleResponse()
        errmsg = self.setSettings("PATH", os.path.dirname(os.path.abspath(path)) + '/')
        if errmsg:
            response.result = "ERROR"
            response.errmsg.append(errmsg)
            return response
        self.mysocket.send_line("ASSEMBLE {}".format(os.path.basename(path)))
        line = self.mysocket.receive_line()
        response.result = line
        if response.result == "ERROR":
            errmsg_list = self.mysocket.receive_lines_till_eof()
            response.errmsg = "\n".join(errmsg_list)
        return response
