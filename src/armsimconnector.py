#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of Qt ARMSim, (C) 2014 by Sergio Barrachina Mir.     #
#                                                                         #
#  Qt ARMSim is free software; you can redistribute it and/or modify      #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 2 of the License, or      #
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


class ARMSimConnector():
    
    def __init__(self, command, port, server="localhost"):
        self.command = command
        self.armsim_pid = None
        self.mysocket = MySocket()
        self.server = server
        self.port = port
        self.connected = False
        self.current_port = None
        self.version = None
        # Regular expressions
        self.re_regexpr = re.compile("r([0-9]+): (0[xX][0-9a-fA-F]+)")
        
    def connect(self):
        """
        Connects with ARMSim.
        
        @return: errmsg     An error msg if an error occurred, None otherwise   
        """
        # 1) Search if ARMSim is already listening in a port in the range [self.port, self.port+10[
        for port in range(self.port, self.port+10):
            try:
                self.mysocket.connect_to(port, server=self.server)
                self.mysocket.sock.settimeout(2.0) # Set timeout to 2 seconds
            except ConnectionRefusedError:
                continue
            if self.getVersion():
                self.connected = True
                self.current_port = port
                return None
        if self.server != "localhost":
            return "Could not connect to ARMSim server at {}:{}-{}".format(self.server, self.port, self.port+10)
        # 2) Else, if server == "localhost", then launch a new copy of ARMSim 
        self.armsim_pid = subprocess.Popen(["ruby",
                                            self.command, 
                                            str(self.port)],
                                            cwd = os.path.dirname(self.command)
                                           ).pid
        if not self.armsim_pid:
            return "Could not launch ARMSim command"
        chances = 3
        while chances:
            try:
                self.mysocket.connect_to(self.port)
                self.mysocket.sock.settimeout(2.0) # Set timeout to 2 seconds
                break
            except ConnectionRefusedError:
                # Sleep half a second while the server gets ready
                time.sleep(.5)
                chances -= 1
        if chances == 0:
            return "ARMSim refused to open a connection at port {}.".format(self.port)
        if not self.getVersion():
            return "ARMSim could be listening at port {}, but it does not answer as expected.".format(self.port)

        self.connected = True
        self.current_port = self.port
        return None

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
            try:
                (reg, hex_value) = self.re_regexpr.search(line).groups()
            except AttributeError:
                print("ERROR: Register not found at '{}'!".format(line))
                raise
            registers.append((int(reg), hex_value))
        return registers
