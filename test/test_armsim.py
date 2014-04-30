#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Fake armsim. Used to try socket communication between qarmsim and
# armsim while defining its grammar.

import sys
import getopt
import string
from src.mysocket import MySocket
import unittest

PORT = 8010

def myhelp():
    print("""Usage: test_armsim.py

This application is used to test the communication between qarmsim and
the simulator. Before running this test, the simulator has to be
already running and listening in the port {}.

Options:
   -v, --verbose     increment the output verbosity
   -h, --help        display this help and exit

Please, report bugs to <barrachi@uji.es>.
""".format(PORT))

def ERROR(text):
    "Prints an error message and exits with a -1 value."
    sys.stderr.write("ERROR: {}\n".format(text))
    sys.exit(-1)

def getopts():
    "Processes the options passed to the executable"
    optlist, args = getopt.getopt(sys.argv[1:], \
                                  'h', \
                                  ['help', ])
    for opt, arg in optlist:
        if opt in ('-h', '--help'):
            myhelp()
            sys.exit()


mysocket = MySocket()
OK = 'OK'
reg_names = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
             'PC', 'SP', 'LR', 'CPSR']

class TestCommunication(unittest.TestCase):

    def setUp(self):
        "This gets executed before each test"
        mysocket.send_line("RESET REGISTERS")
        mysocket.send_line("RESET MEMORY")
        pass

    def test_reset_registers(self):
        "RESET REGISTERS should reset all registers to their initial value."
        for reg_name in reg_names:
            mysocket.send_line("SET REGISTER {} 0x12345678".format(reg_name)) 
        mysocket.send_line("RESET REGISTERS")
        self.assertEqual(mysocket.receive_line(), OK)
        # Check that r0 is reset to 0x00000000
        mysocket.send_line("SHOW REGISTER {}".format('r0'))
        self.assertEqual(mysocket.receive_line(), "r0: 0x00000000")
        # Check that all the registers have a value different of 0x12345678
        for reg_name in reg_names:
            mysocket.send_line("SHOW REGISTER {}".format(reg_name))
            answer = mysocket.receive_line()
            (reg, value) = answer.split(": ")
            self.assertNotEqual(value, "0x00000000")
        

    def test_dump_registers(self):
        "DUMP REGISTERS should return the value of all the registers."
        
    def test_set_register_1(self):
        "SET REGISTER 1 0x00000005 should overwrite register R1 with 0x00000005."
        mysocket.send_line("SET REGISTER 1 0x00000005")
        mysocket.send_line("SHOW REGISTER 1")
        line = mysocket.receive_line()
        self.assertEqual(line, "0x00000004")

    def test_show_register_r0(self):
        "SHOW REGISTER r0 should return value 0x00000000 after RESET REGISTERS"
        mysocket.send_line("SHOW REGISTER r0")
        line = mysocket.receive_line()
        self.assertEqual(line, "r0: 0x00000000")

    def test_show_version(self):
        "SHOW VERSION should return one or more lines ended by an EOF line."
        mysocket.send_line("SHOW VERSION")
        mysocket.sock.settimeout(2.0) # Set timeout to 2 seconds
        line = ''
        while line != 'EOF':
            line = mysocket.receive_line()
        mysocket.sock.settimeout(None) # Set blocking mode again
            
    def tearDown(self):
        "This gets executed after each test"
        pass
        

if __name__ == '__main__':
    getopts()
    mysocket.connect_to(PORT)
    print("Please, manually check that the simulator has also finished after running all the tests.")
    unittest.main()
    mysocket.close_connection()
    mysocket.close_socket()
