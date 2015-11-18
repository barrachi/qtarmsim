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


import getopt
import sys
import unittest

from .. comm.mysocket import MySocket

PORT = 8010

def myhelp():
    print("""Usage: test_armsim.py

This application is used to test the communication between QtARMSim and
the simulator. Before running this test, the simulator has to be
already running and listening in the port {}.

Options:
   -h, --help        display this help and exit

Please, report bugs to <barrachi@uji.es>.
""".format(PORT))

def ERROR(text):
    "Prints an error message and exits with a -1 value."
    sys.stderr.write("ERROR: {}\n".format(text))
    sys.exit(-1)

def getopts():
    "Processes the options passed to the executable"
    optlist, args = getopt.getopt(sys.argv[1:], # @UnusedVariable
                                  'h',
                                  ['help', ])
    for opt, arg in optlist:  # @UnusedVariable
        if opt in ('-h', '--help'):
            myhelp()
            sys.exit()


OK = 'OK'
EOF = 'EOF'
#reg_names = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
#             'PC', 'SP', 'LR', 'CPSR']
reg_names = ['r{}'.format(x) for x in range(16)]

class CommunicationTestCase(unittest.TestCase):

    #===========================================================================
    # Pre and post test actions         
    #===========================================================================

    def setUp(self):
        "This is executed before each one of the tests"
        self.mysocket = MySocket()
        try:
            self.mysocket.connect_to(PORT)
        except ConnectionRefusedError:
            ERROR("Couldn't connect to the simulator. Please, check that the simulator\n"
                  "       is listening on port {}.".format(PORT))
        # Usual operation will be blocking(?), but here we put the timeout to 2 seconds
        self.mysocket.sock.settimeout(2.0) # Set timeout to 2 seconds
        self.mysocket.send_line("RESET REGISTERS")
        if (self.mysocket.receive_line() != OK):
            ERROR('RESET REGISTERS should return an OK')
        self.mysocket.send_line("RESET MEMORY")
        if (self.mysocket.receive_line() != OK):
            ERROR('RESET MEMORY should return an OK')

    def tearDown(self):
        "This gets executed after each test"
        self.mysocket.close_connection()
        self.mysocket.close_socket()

    
    #===========================================================================
    # Show version test         
    #===========================================================================

    def test_show_version(self):
        "SHOW VERSION should return one or more lines ended by an EOF line."
        self.mysocket.send_line("SHOW VERSION")
        line = ''
        while line != 'EOF':
            line = self.mysocket.receive_line()
        self.assertEqual(line, EOF)

    
    #===========================================================================
    # Register tests         
    #===========================================================================
    
    def test_show_register_r0(self):
        "SHOW REGISTER r0 should return 'r0: 0x00000000' after RESET REGISTERS"
        self.mysocket.send_line("SHOW REGISTER r0")
        self.assertEqual(self.mysocket.receive_line(), "r0: 0x00000000")

    def test_set_register_r1(self):
        "SET REGISTER 1 WITH 0x00000005 should overwrite register r1 with 0x00000005 and return OK."
        self.mysocket.send_line("SET REGISTER r1 WITH 0x00000005")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SHOW REGISTER r1")
        self.assertEqual(self.mysocket.receive_line(), "r1: 0x00000005")

    def test_reset_registers(self):
        "RESET REGISTERS should reset all registers to their initial value."
        for reg_name in reg_names:
            self.mysocket.send_line("SET REGISTER {} WITH 0x12345678".format(reg_name)) 
            self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("RESET REGISTERS")
        self.assertEqual(self.mysocket.receive_line(), OK)
        # Check that r0 is reset to 0x00000000
        self.mysocket.send_line("SHOW REGISTER r0")
        self.assertEqual(self.mysocket.receive_line(), "r0: 0x00000000")
        # Check that the rest of the registers have a value different of 0x12345678
        for reg_name in reg_names[1:]:
            self.mysocket.send_line("SHOW REGISTER {}".format(reg_name))
            answer = self.mysocket.receive_line()
            value = answer.split(": ")[1]
            self.assertNotEqual(value, "0x12345678")
         
    def test_dump_registers(self):
        "DUMP REGISTERS should return the value of all the registers."
        self.mysocket.send_line("DUMP REGISTERS")
        for reg_name in reg_names:
            line = self.mysocket.receive_line()
            part_tested = "{}: 0x".format(reg_name)
            self.assertEqual(line[:len(part_tested)], part_tested)

    #===========================================================================
    # Memory tests         
    #===========================================================================
    
    def test_show_memory_byte(self):
        "SHOW MEMORY BYTE AT 0x20070020 should return '0x20070020: 0x00' after RESET MEMORY"
        self.mysocket.send_line("SHOW MEMORY BYTE AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x00")

    def test_show_memory_half(self):
        "SHOW MEMORY HALF AT 0x20070020 should return '0x20070020: 0x0000' after RESET MEMORY"
        self.mysocket.send_line("SHOW MEMORY HALF AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x0000")

    def test_show_memory_word(self):
        "SHOW MEMORY WORD AT 0x20070020 should return '0x20070020: 0x00000000' after RESET MEMORY"
        self.mysocket.send_line("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x00000000")

    def test_set_memory_byte(self):
        "SET MEMORY BYTE AT 0x20070020 WITH 0X10 should overwrite that byte with 0x10 and return OK."
        self.mysocket.send_line("SET MEMORY BYTE AT 0x20070020 WITH 0x10")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SHOW MEMORY BYTE AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x10")

    def test_set_memory_half(self):
        "SET MEMORY HALF AT 0x20070020 WITH 0X1020 should overwrite that half with 0x1020 and return OK."
        self.mysocket.send_line("SET MEMORY HALF AT 0x20070020 WITH 0x1020")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SHOW MEMORY HALF AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x1020")

    def test_set_memory_word(self):
        "SET MEMORY WORD AT 0x20070020 WITH 0X10203040 should overwrite that word with 0x10203040 and return OK."
        self.mysocket.send_line("SET MEMORY WORD AT 0x20070020 WITH 0x10203040")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x10203040")

    def test_endianess(self):
        "Check that little-endian is being used for storing halfs and words."
        self.mysocket.send_line("SET MEMORY BYTE AT 0x20070020 WITH 0x10")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SET MEMORY BYTE AT 0x20070021 WITH 0x20")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SET MEMORY BYTE AT 0x20070022 WITH 0x30")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SET MEMORY BYTE AT 0x20070023 WITH 0x40")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SHOW MEMORY HALF AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x2010")
        self.mysocket.send_line("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x40302010")
        self.mysocket.send_line("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mysocket.receive_line(), "0x20070020: 0x40302010")

    def test_reset_memory(self):
        "RESET MEMORY should reset all the memory to its initial value."
        for pos in range(537329664, 537329664+20): # From 0x20070000
            hex_pos = "0x{0:0{1}X}".format(pos, 8)
            self.mysocket.send_line("SET MEMORY BYTE AT {} WITH {}".format(hex_pos, "0xA0"))
            self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("RESET MEMORY")
        self.assertEqual(self.mysocket.receive_line(), OK)
        # Check that the read bytes a value different of 0xA0
        for pos in range(537329664, 537329664+20):
            hex_pos = "0x{0:0{1}X}".format(pos, 8)
            self.mysocket.send_line("SHOW MEMORY BYTE AT {}".format(hex_pos))
            answer = self.mysocket.receive_line()
            value = answer.split(": ")[1]
            self.assertNotEqual(value, "0xA0")

    def test_dump_memory(self):
        "DUMP MEMORY start_address nbytes should return the value of the nbytes from start_address."
        self.mysocket.send_line("DUMP MEMORY 0x20070000 20")
        for pos in range(537329664, 537329664+20): # From 0x20070000
            hex_pos = "0x{0:0{1}X}".format(pos, 8)
            self.assertEqual(self.mysocket.receive_line(), "{}: 0x00".format(hex_pos))
        self.assertEqual(self.mysocket.receive_line(), "EOF")
        #self.assertRaises(socket.timeout, self.mysocket.receive_line)

    #===========================================================================
    # Breakpoint tests         
    #===========================================================================
    
    def test_breakpoints(self):
        "Test clear, set, and show breakpoints"
        #--------------------------------------------------
        # Method used to get the breakpoints from the simmulator
        #--------------------------------------------------
        def get_breakpoints():
            line = ''
            sim_breakpoints = []
            self.mysocket.send_line("SHOW BREAKPOINTS")
            while (line != EOF):
                line = self.mysocket.receive_line()
                if line != EOF:
                    self.assertEqual(line[:2], "0x")
                    sim_breakpoints.append(line)
            return sim_breakpoints
        #--------------------------------------------------
        # "Clear breakpoints" test (firs pass)
        #--------------------------------------------------
        self.mysocket.send_line("CLEAR BREAKPOINTS")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SHOW BREAKPOINTS")
        self.assertEqual(self.mysocket.receive_line(), EOF, "Expecting EOF after SHOW BREAKPOINTS")
        #--------------------------------------------------
        # "Set breakpoint" at test        
        #--------------------------------------------------
        breakpoints = ["0x10102020", "0x20203030", "0x30304040"]
        for breakpoint in breakpoints:
            self.mysocket.send_line("SET BREAKPOINT AT {}".format(breakpoint))
            self.assertEqual(self.mysocket.receive_line(), OK)
        sim_breakpoints = get_breakpoints()
        self.assertCountEqual(sim_breakpoints, breakpoints, "Stored breakpoints differ from setted ones")
        #--------------------------------------------------
        # "Clear breakpoint at" test
        #--------------------------------------------------
        self.mysocket.send_line("CLEAR BREAKPOINT AT 0x10102020")
        self.assertEqual(self.mysocket.receive_line(), OK, "Expecting OK after CLEAR BREAKPOINT AT 0x10102020")
        breakpoints.remove("0x10102020")
        sim_breakpoints = get_breakpoints()
        self.assertCountEqual(sim_breakpoints, breakpoints, "Stored breakpoints differ from setted ones after removing the one at address 0x101012020")
        #--------------------------------------------------
        # "Clear breakpoints" test (second pass)
        #--------------------------------------------------
        self.mysocket.send_line("CLEAR BREAKPOINTS")
        self.assertEqual(self.mysocket.receive_line(), OK)
        self.mysocket.send_line("SHOW BREAKPOINTS")
        self.assertEqual(self.mysocket.receive_line(), EOF, "Expecting EOF after SHOW BREAKPOINTS")        
        
        
        
    #===========================================================================
    # Disassemble tests         
    #===========================================================================
    
    #===========================================================================
    # Execute tests         
    #===========================================================================
    
    #===========================================================================
    # Assemble tests         
    #===========================================================================
    

def suite():
    '''
    Used to manually define the suite of tests that should be executed.
    '''
    # To check specific tests, change manual_suite to True and add as addTest
    # lines are required.
    manual_suite = True
    if manual_suite:
        suite = unittest.TestSuite()
        suite.addTest(CommunicationTestCase('test_show_version'))
        suite.addTest(CommunicationTestCase('test_show_register_r0'))
        suite.addTest(CommunicationTestCase('test_set_register_r1'))
        
        suite.addTest(CommunicationTestCase('test_reset_registers'))
        suite.addTest(CommunicationTestCase('test_show_memory_byte'))
        suite.addTest(CommunicationTestCase('test_show_memory_half'))
        suite.addTest(CommunicationTestCase('test_show_memory_word'))
        suite.addTest(CommunicationTestCase('test_endianess'))
        suite.addTest(CommunicationTestCase('test_reset_memory'))

        suite.addTest(CommunicationTestCase('test_dump_registers'))
        suite.addTest(CommunicationTestCase('test_set_memory_byte'))
        suite.addTest(CommunicationTestCase('test_set_memory_half'))
        suite.addTest(CommunicationTestCase('test_set_memory_word'))
        
        suite.addTest(CommunicationTestCase('test_dump_memory'))
        suite.addTest(CommunicationTestCase('test_breakpoints'))
        return suite
    else:
        return None        


if __name__ == '__main__':
    getopts()
    if suite():
        unittest.TextTestRunner().run(suite())
    else:
        unittest.main()        
