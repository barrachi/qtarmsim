#!/usr/bin/env python3
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

# This application can be used to try socket communication between QtARMSim and
# ARMSim while defining the communication grammar.

import sys
import getopt

from .. comm.mysocket import MySocket

# Globals
PORT = 0
mysocket = None

def myhelp():
    print("""Usage: fake_armsim.py -p PORTNUMBER

This is a fake ARMSim with socket server capabilities. Please, use the -p option
to indicate which port number should be used.

Options:
   -v, --verbose     increment the output verbosity
   -h, --help        display this help and exit

Please, report bugs to <barrachi@uji.es>.
""")

def ERROR(text):
    "Prints an error message and exits with a -1 value."
    sys.stderr.write("ERROR: {}\n".format(text))
    sys.exit(-1)

def getopts():
    "Processes the options passed to the executable"
    global PORT
    optlist, args = getopt.getopt(sys.argv[1:],         # @UnusedVariable
                                  'p:h',
                                  ['port:', 'help', ])
    for opt, arg in optlist:
        if opt in ('-h', '--help'):
            myhelp()
            sys.exit()
        elif opt in ('-p', '--port'):
            PORT = int(arg)
    if PORT == 0:
        myhelp()
        ERROR("a port number must be specified.")

# Fake registers
reg_names = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
             'PC', 'SP', 'LR', 'CPSR']
_REGISTERS = {
    'r0': "0x00000000",
    'r1': "0x00000000",
    'r2': "0x00000000",
    'r3': "0x00000000",
    'r4': "0x00000000",
    'r5': "0x00000000",
    'r6': "0x00000000",
    'r7': "0x00000000",
    'PC': "0x00000000",
    'SP': "0x00000000",
    'LR': "0x00000000",
    'CPSR': "0x00000000",
    }
REGISTERS = _REGISTERS.copy()

# Fake memory
_MEMORY = ["0x00"]*10000
MEMORY = _MEMORY[:]

# Fake breakpoints
BREAKPOINTS = []

# Literals
OK = 'OK'
EOF = 'EOF'


#===============================================================================
# SHOW commands
#===============================================================================

def do_SHOW_VERSION(args, socket):
    print("Showing version information")
    socket.send_line("Fake ARMSim version 0.1")
    socket.send_line("(c) 2014 Sergio Barrachina Mir")
    socket.send_line(EOF)

def do_SHOW_REGISTER(args, socket):
    reg_name = args[2]
    print("Showing contents of register {} ({})".format(reg_name, REGISTERS[reg_name]))
    socket.send_line("{}: {}".format(reg_name, REGISTERS[reg_name]))

def do_SHOW_MEMORY(args, socket):
    "SHOW MEMORY (BYTE|HALF|WORD) AT ADDRESS"
    size = args[2]
    hex_address = args[4]
    print("Showing {} at Memory[{}]".format(size.lower(), hex_address))
    address = int(hex_address, 16)
    if size == 'BYTE':
        socket.send_line("{}: {}".format(hex_address, MEMORY[address]))
    elif size == 'HALF':
        # Little-endian version
        value = MEMORY[address] + MEMORY[address+1][2:]
        socket.send_line("{}: {}".format(hex_address, value))
    elif size == 'WORD':
        # Little-endian version
        value = MEMORY[address] + MEMORY[address+1][2:] + MEMORY[address+2][2:] + MEMORY[address+3][2:]
        socket.send_line("{}: {}".format(hex_address, value))
    
def do_DUMP_REGISTERS(args, socket):
    print("Dumping all the registers")
    for reg_name in reg_names:
        socket.send_line("{}: {}".format(reg_name, REGISTERS[reg_name]))

def do_DUMP_MEMORY(args, socket):
    "DUMP MEMORY START_ADDRESS NBYTES"
    start = int(args[2], 16)
    nbytes = int(args[3])  
    print("Dumping memory starting at address {} ({} bytes)".format(start, nbytes))
    for pos in range(start, start+nbytes):
        socket.send_line("{}: {}".format("0x{0:0{1}X}".format(pos, 8), MEMORY[pos]))

def do_SHOW_BREAKPOINTS(args, socket):
    "SHOW BREAKPOINTS"
    print("Showing breakpoints")
    for breakpoint in BREAKPOINTS:
        socket.send_line(breakpoint)
    socket.send_line(EOF)


#===============================================================================
# SET commands
#===============================================================================

def do_SET_REGISTER(args, socket):
    "SET REGISTER regname WITH hexvalue"
    reg_name = args[2]
    value = args[4]
    print("Setting register {} to {}".format(reg_name, value))
    REGISTERS[reg_name] = value
    socket.send_line(OK)

def do_SET_MEMORY(args, socket):
    "SET MEMORY (BYTE|HALF|WORD) AT address WITH hexvalue"
    size = args[2]
    hex_pos = args[4]
    pos = int(hex_pos, 16)
    value = args[6]
    print("Setting {} at memory[{}] to {}".format(size.lower(), hex_pos, value))
    if size == 'BYTE':
        MEMORY[pos] = value
    elif size == 'HALF':
        MEMORY[pos] = value[:4]
        MEMORY[pos+1] = "0x{}".format(value[4:])
    elif size == 'WORD':
        MEMORY[pos] = value[:4]
        MEMORY[pos+1] = "0x{}".format(value[4:6])
        MEMORY[pos+2] = "0x{}".format(value[6:8])
        MEMORY[pos+3] = "0x{}".format(value[8:])
    socket.send_line(OK)
        
def do_SET_BREAKPOINT_AT(args, socket):
    "SET BREAKPOINT AT address"
    breakpoint = args[3]
    print("Setting breakpoint at {}".format(breakpoint))
    BREAKPOINTS.append(breakpoint)
    socket.send_line(OK)

#===============================================================================
# RESET commands
#===============================================================================

def do_RESET_REGISTERS(args, socket):
    global REGISTERS
    print("Reseting registers")
    REGISTERS = _REGISTERS.copy()
    socket.send_line(OK)

def do_RESET_MEMORY(args, socket):
    global MEMORY
    print("Reseting memory")
    MEMORY = _MEMORY[:]
    socket.send_line(OK)

#===============================================================================
# CLEAR commands
#===============================================================================

def do_CLEAR_BREAKPOINTS(args, socket):
    "CLEAR BREAKPOINTS"
    global BREAKPOINTS
    print("Clearing breakpoints")
    BREAKPOINTS = []
    socket.send_line(OK)
    
def do_CLEAR_BREAKPOINT_AT(args, socket):
    "CLEAR BREAKPOINT AT"
    breakpoint = args[3]
    print("Clearing breakpoint at {}".format(breakpoint))
    BREAKPOINTS.remove(breakpoint)
    socket.send_line(OK)

#===============================================================================
# def signal_handler(signal, frame):
#     if mysocket != None:
#         mysocket.close_socket()
#     sys.exit(0)
#===============================================================================

def main():
    "Main part of the application"
    getopts()
    #signal.signal(signal.SIGINT, signal_handler)
    mysocket = MySocket(verbose = True)
    mysocket.server_bind(PORT)
    while True:
        print("")
        mysocket.server_accept_connection()
        lines_generator = mysocket.get_lines()
        for line in lines_generator:
            args = line.split(' ')
            for n in range(len(args), 0, -1):
                do_method_name = 'do_{}'.format('_'.join(args[0:n]))
                do_method = globals().get(do_method_name)
                if do_method:
                    do_method(args, mysocket)
                    break
            else:
                print(">>> Unsupported command: {}".format(line))
    mysocket.close_connection()
    mysocket.close_socket()

if __name__ == "__main__":
    main()
