#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Fake armsim. Used to try socket communication between qarmsim and
# armsim while defining its grammar.

import sys
import getopt
import string
from mysocket import MySocket

PORT = 0

def myhelp():
    print("""Usage: fake_armsim.py -p PORTNUMBER

This is a fake armsim with socket server capabilities. Please, use the
-p option to indicate which port number should be used.

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
    optlist, args = getopt.getopt(sys.argv[1:], \
                                  'p:h', \
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


REGISTERS = ["0x00000000"]*16
MEMORY = ["0x00"]*10000

def do_SHOW_VERSION(args, socket):
    print("Showing version information")
    socket.send_line("fake_armsim version 0.1")
    socket.send_line("(c) 2014 Sergio Barrachina Mir")
    socket.send_line("EOF")

def do_SHOW_REGISTER(args, socket):
    reg = int(args[2])
    print("Showing contents of register {}".format(reg))
    socket.send_line(REGISTERS[reg])
    
def do_DUMP_REGISTERS(args, socket):
    print("Dumping all the registers")
    for reg in range(len(REGISTERS)):
        socket.send_line(REGISTERS[reg])

def do_DUMP_MEMORY(args, socket):
    start = int(args[2])
    nbytes = int(args[3])    
    print("Dumping memory starting at address {} ({} bytes)".format(start, nbytes))
    for pos in range(start, start+nbytes+1):
        socket.send_line(MEMORY[pos])

def do_SET_REGISTER(args, socket):
    reg = int(args[2])
    value = args[3]
    print("Setting register {} to {}".format(reg, value))
    REGISTERS[reg] = value

def do_SET_MEMORY(args, socket):
    pos = int(args[2])
    value = args[3]
    print("Setting memory[{}] to {}".format(pos, value))
    MEMORY[pos] = value

def do_CLEAR_REGISTERS(args, socket):
    for reg in range(0,16):
        REGISTERS[reg]="0x00000000"
        
def main():
    "Main part of the application"
    getopts()
    mysocket = MySocket()
    mysocket.server_bind(PORT)
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
