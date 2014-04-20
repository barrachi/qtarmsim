#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Fake armsim. Used to try socket communication between qarmsim and
# armsim while defining its grammar.

import sys
import getopt
import string
from mysocket import MySocket
import unittest

PORT = 8011

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

class TestCommunication(unittest.TestCase):

    def setUp(self):
        "This gets executed before each test"
        mysocket.send_line("CLEAR REGISTERS")
        mysocket.send_line("CLEAR MEMORY")
        pass

    def test_clear_registers(self):
        "CLEAR REGISTERS should reset all registers."
        for reg in range(16):
            mysocket.send_line("SET REGISTER {} 0x00000005".format(reg)) 
        mysocket.send_line("CLEAR REGISTERS")
        for reg in range(16):
            mysocket.send_line("SHOW REGISTER {}".format(reg))
            self.assertEqual(mysocket.receive_line(), "0x00000000")
        

    def test_dump_registers(self):
        "DUMP REGISTERS should return the value of all the registers."
        
    def test_set_register_1(self):
        "SET REGISTER 1 0x00000005 should overwrite register R1 with 0x00000005."
        mysocket.send_line("SET REGISTER 1 0x00000005")
        mysocket.send_line("SHOW REGISTER 1")
        line = mysocket.receive_line()
        self.assertEqual(line, "0x00000000")

    def test_show_register_0(self):
        "SHOW REGISTER 0 should return value 0x00000000 after CLEAR REGISTERS"
        mysocket.send_line("SHOW REGISTER 0")
        line = mysocket.receive_line()
        self.assertEqual(line, "0x00000000")

        # should raise an exception for an immutable sequence
        #self.assertRaises(TypeError, random.shuffle, (1,2,3))

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
        
    # def test_choice(self):
    #     element = random.choice(self.seq)
    #     self.assertTrue(element in self.seq)

    # def test_sample(self):
    #     with self.assertRaises(ValueError):
    #         random.sample(self.seq, 20)
    #     for element in random.sample(self.seq, 5):
    #         self.assertTrue(element in self.seq)


if __name__ == '__main__':
    getopts()
    mysocket.connect_to(PORT)
    print("Please, manually check that the simulator has also finished after running all the tests.")
    unittest.main()
    mysocket.close_connection()
    mysocket.close_socket()
