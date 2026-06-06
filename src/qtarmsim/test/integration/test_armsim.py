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


# pyright: reportAttributeAccessIssue=false
# MySocket inherits from QObject (Shiboken.Object), whose metaclass prevents basedpyright
# from resolving instance methods on subclasses. All method accesses here are correct at runtime.

import getopt
import os
import shutil
import sys
import unittest

from ...comm.mysocket import MySocket

PORT = 8010
ORIG_CODE = 0x00180000
TEST_DIR = os.path.dirname(os.path.abspath(__file__))


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
    """Prints an error message and exits with a -1 value."""
    sys.stderr.write("ERROR: {}\n".format(text))
    sys.exit(-1)


def getopts():
    """Processes the options passed to the executable"""
    optlist, _ = getopt.getopt(sys.argv[1:],
                               'h',
                               ['help', ])
    for opt, _ in optlist:
        if opt in ('-h', '--help'):
            myhelp()
            sys.exit()


OK = 'OK'
EOF = 'EOF'
# reg_names = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7',
#             'PC', 'SP', 'LR', 'CPSR']
reg_names = ['r{}'.format(x) for x in range(16)]


class CommunicationTestCase(unittest.TestCase):

    mySocket: MySocket

    # ===========================================================================
    # Pre and post test actions
    # ===========================================================================

    def setUp(self):
        """This is executed before each one of the tests"""
        self.mySocket = MySocket()
        try:
            self.mySocket.connectTo(PORT)
        except ConnectionRefusedError:
            self.mySocket.closeConnection()
            self.skipTest("Couldn't connect to the simulator on port {}".format(PORT))
        self.mySocket.setConnTimeout(2.0)
        self.mySocket.sendLine("RESET REGISTERS")
        if self.mySocket.receiveLine() != OK:
            ERROR('RESET REGISTERS should return an OK')
        self.mySocket.sendLine("RESET MEMORY")
        if self.mySocket.receiveLine() != OK:
            ERROR('RESET MEMORY should return an OK')

    def tearDown(self):
        """This gets executed after each test"""
        self.mySocket.closeConnection()

    # ===========================================================================
    # Show version test         
    # ===========================================================================

    def test_show_version(self):
        """SHOW VERSION should return one or more lines ended by an EOF line."""
        self.mySocket.sendLine("SHOW VERSION")
        line = ''
        while line != 'EOF':
            line = self.mySocket.receiveLine()
        self.assertEqual(line, EOF)

    # ===========================================================================
    # Register tests         
    # ===========================================================================

    def test_show_register_r0(self):
        """SHOW REGISTER r0 should return 'r0: 0x00000000' after RESET REGISTERS"""
        self.mySocket.sendLine("SHOW REGISTER r0")
        self.assertEqual(self.mySocket.receiveLine(), "r0: 0x00000000")

    def test_set_register_r1(self):
        """SET REGISTER 1 WITH 0x00000005 should overwrite register r1 with 0x00000005 and return OK."""
        self.mySocket.sendLine("SET REGISTER r1 WITH 0x00000005")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SHOW REGISTER r1")
        self.assertEqual(self.mySocket.receiveLine(), "r1: 0x00000005")

    def test_reset_registers(self):
        """RESET REGISTERS should reset all registers to their initial value."""
        for reg_name in reg_names:
            self.mySocket.sendLine("SET REGISTER {} WITH 0x12345678".format(reg_name))
            self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("RESET REGISTERS")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        # Check that r0 is reset to 0x00000000
        self.mySocket.sendLine("SHOW REGISTER r0")
        self.assertEqual(self.mySocket.receiveLine(), "r0: 0x00000000")
        # Check that the rest of the registers have a value different of 0x12345678
        for reg_name in reg_names[1:]:
            self.mySocket.sendLine("SHOW REGISTER {}".format(reg_name))
            answer = self.mySocket.receiveLine()
            value = answer.split(": ")[1]
            self.assertNotEqual(value, "0x12345678")

    def test_dump_registers(self):
        """DUMP REGISTERS should return the value of all the registers."""
        self.mySocket.sendLine("DUMP REGISTERS")
        for reg_name in reg_names:
            line = self.mySocket.receiveLine()
            part_tested = "{}: 0x".format(reg_name)
            self.assertEqual(line[:len(part_tested)], part_tested)

    # ===========================================================================
    # Memory tests         
    # ===========================================================================

    def test_show_memory_byte(self):
        """SHOW MEMORY BYTE AT 0x20070020 should return '0x20070020: 0x00' after RESET MEMORY"""
        self.mySocket.sendLine("SHOW MEMORY BYTE AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x00")

    def test_show_memory_half(self):
        """SHOW MEMORY HALF AT 0x20070020 should return '0x20070020: 0x0000' after RESET MEMORY"""
        self.mySocket.sendLine("SHOW MEMORY HALF AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x0000")

    def test_show_memory_word(self):
        """SHOW MEMORY WORD AT 0x20070020 should return '0x20070020: 0x00000000' after RESET MEMORY"""
        self.mySocket.sendLine("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x00000000")

    def test_set_memory_byte(self):
        """SET MEMORY BYTE AT 0x20070020 WITH 0X10 should overwrite that byte with 0x10 and return OK."""
        self.mySocket.sendLine("SET MEMORY BYTE AT 0x20070020 WITH 0x10")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SHOW MEMORY BYTE AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x10")

    def test_set_memory_half(self):
        """SET MEMORY HALF AT 0x20070020 WITH 0X1020 should overwrite that half with 0x1020 and return OK."""
        self.mySocket.sendLine("SET MEMORY HALF AT 0x20070020 WITH 0x1020")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SHOW MEMORY HALF AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x1020")

    def test_set_memory_word(self):
        """SET MEMORY WORD AT 0x20070020 WITH 0X10203040 should overwrite that word with 0x10203040 and return OK."""
        self.mySocket.sendLine("SET MEMORY WORD AT 0x20070020 WITH 0x10203040")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x10203040")

    def test_endianess(self):
        """Check that little-endian is being used for storing halfs and words."""
        self.mySocket.sendLine("SET MEMORY BYTE AT 0x20070020 WITH 0x10")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SET MEMORY BYTE AT 0x20070021 WITH 0x20")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SET MEMORY BYTE AT 0x20070022 WITH 0x30")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SET MEMORY BYTE AT 0x20070023 WITH 0x40")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SHOW MEMORY HALF AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x2010")
        self.mySocket.sendLine("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x40302010")
        self.mySocket.sendLine("SHOW MEMORY WORD AT 0x20070020")
        self.assertEqual(self.mySocket.receiveLine(), "0x20070020: 0x40302010")

    def test_reset_memory(self):
        """RESET MEMORY should reset all the memory to its initial value."""
        for pos in range(537329664, 537329664 + 20):  # From 0x20070000
            hex_pos = "0x{0:0{1}X}".format(pos, 8)
            self.mySocket.sendLine("SET MEMORY BYTE AT {} WITH {}".format(hex_pos, "0xA0"))
            self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("RESET MEMORY")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        # Check that the read bytes a value different of 0xA0
        for pos in range(537329664, 537329664 + 20):
            hex_pos = "0x{0:0{1}X}".format(pos, 8)
            self.mySocket.sendLine("SHOW MEMORY BYTE AT {}".format(hex_pos))
            answer = self.mySocket.receiveLine()
            value = answer.split(": ")[1]
            self.assertNotEqual(value, "0xA0")

    def test_dump_memory(self):
        """DUMP MEMORY start_address nbytes should return the value of the nbytes from start_address."""
        self.mySocket.sendLine("DUMP MEMORY 0x20070000 20")
        for pos in range(537329664, 537329664 + 20):  # From 0x20070000
            hex_pos = "0x{0:0{1}X}".format(pos, 8)
            self.assertEqual(self.mySocket.receiveLine(), "{}: 0x00".format(hex_pos))
        self.assertEqual(self.mySocket.receiveLine(), "EOF")
        # self.assertRaises(socket.timeout, self.mysocket.receive_line)

    # ===========================================================================
    # Breakpoint tests         
    # ===========================================================================

    def test_breakpoints(self):
        """Test clear, set, and show breakpoints"""

        # --------------------------------------------------
        # Method used to get the breakpoints from the simmulator
        # --------------------------------------------------
        def get_breakpoints():
            line = ''
            breakpoints_ = []
            self.mySocket.sendLine("SHOW BREAKPOINTS")
            while line != EOF:
                line = self.mySocket.receiveLine()
                if line != EOF:
                    self.assertEqual(line[:2], "0x")
                    breakpoints_.append(line)
            return breakpoints_

        # --------------------------------------------------
        # "Clear breakpoints" test (firs pass)
        # --------------------------------------------------
        self.mySocket.sendLine("CLEAR BREAKPOINTS")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SHOW BREAKPOINTS")
        self.assertEqual(self.mySocket.receiveLine(), EOF, "Expecting EOF after SHOW BREAKPOINTS")
        # --------------------------------------------------
        # "Set breakpoint" at test        
        # --------------------------------------------------
        breakpoints = ["0x10102020", "0x20203030", "0x30304040"]
        for breakpoint_ in breakpoints:
            self.mySocket.sendLine("SET BREAKPOINT AT {}".format(breakpoint_))
            self.assertEqual(self.mySocket.receiveLine(), OK)
        sim_breakpoints = get_breakpoints()
        self.assertCountEqual(sim_breakpoints, breakpoints, "Stored breakpoints differ from setted ones")
        # --------------------------------------------------
        # "Clear breakpoint at" test
        # --------------------------------------------------
        self.mySocket.sendLine("CLEAR BREAKPOINT AT 0x10102020")
        self.assertEqual(self.mySocket.receiveLine(), OK, "Expecting OK after CLEAR BREAKPOINT AT 0x10102020")
        breakpoints.remove("0x10102020")
        sim_breakpoints = get_breakpoints()
        self.assertCountEqual(sim_breakpoints, breakpoints,
                              "Stored breakpoints differ from setted ones after removing the one at address 0x101012020")
        # --------------------------------------------------
        # "Clear breakpoints" test (second pass)
        # --------------------------------------------------
        self.mySocket.sendLine("CLEAR BREAKPOINTS")
        self.assertEqual(self.mySocket.receiveLine(), OK)
        self.mySocket.sendLine("SHOW BREAKPOINTS")
        self.assertEqual(self.mySocket.receiveLine(), EOF, "Expecting EOF after SHOW BREAKPOINTS")

        # ===========================================================================
    # Disassemble tests
    # ===========================================================================

    # ===========================================================================
    # Execute tests
    # ===========================================================================

    # ===========================================================================
    # Assemble tests
    # ===========================================================================


# ===========================================================================
# Base class for tests that require an assembled program
# ===========================================================================

class _BaseSimulatorTest(unittest.TestCase):
    """
    Base class for tests that require a running server with an assembled program.
    setUpClass assembles add.s once for the whole class via a temporary connection.
    Each test method gets its own connection with registers reset.
    """

    mySocket: MySocket

    @classmethod
    def setUpClass(cls):
        sock: MySocket = MySocket()
        try:
            sock.connectTo(PORT)
        except ConnectionRefusedError:
            sock.closeConnection()
            raise unittest.SkipTest("Server not running on port {}".format(PORT))
        try:
            sock.setConnTimeout(5.0)  # pyright: ignore[reportOptionalMemberAccess]
            sock.sendLine("CONFIG PATH {}".format(TEST_DIR))
            if sock.receiveLine() != OK:
                raise unittest.SkipTest("CONFIG PATH failed")
            sock.sendLine("ASSEMBLE add.s")
            if sock.receiveLine() != 'SUCCESS':
                raise unittest.SkipTest("ASSEMBLE add.s failed (check arm-none-eabi-gcc is available)")
        finally:
            sock.closeConnection()

    def setUp(self):
        self.mySocket: MySocket = MySocket()
        try:
            self.mySocket.connectTo(PORT)
        except ConnectionRefusedError:
            self.mySocket.closeConnection()
            self.skipTest("Server not running on port {}".format(PORT))
        self.mySocket.setConnTimeout(2.0)  # pyright: ignore[reportOptionalMemberAccess]
        self.mySocket.sendLine("RESET REGISTERS")
        if self.mySocket.receiveLine() != OK:
            ERROR('RESET REGISTERS should return an OK')

    def tearDown(self):
        self.mySocket.closeConnection()

    def _receive_till_eof(self) -> list[str]:
        """Receives lines until EOF; returns them without the EOF sentinel."""
        lines = []
        while True:
            line = self.mySocket.receiveLine()
            if line == EOF:
                break
            lines.append(line)
        return lines

    def _parse_execute_response(self) -> tuple[str, str, dict[str, int], dict[int, int], str]:
        """
        Reads a complete EXECUTE response and returns:
          (status, disasm_line, registers, memory, error_msg)
        where registers maps "r0"/"r15"/... -> int value,
        and memory maps address_int -> byte_int.
        """
        lines = self._receive_till_eof()
        status  = lines[0] if lines else ''
        disasm  = lines[1] if len(lines) > 1 else ''
        registers: dict[str, int] = {}
        memory:    dict[int, int] = {}
        error_msg = ''
        mode = ''
        for line in lines[2:]:
            if line in ('AFFECTED REGISTERS', 'AFFECTED MEMORY', 'ERROR MESSAGE'):
                mode = line
            elif mode == 'AFFECTED REGISTERS':
                # "r0: 0x00000005"
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    registers[parts[0]] = int(parts[1], 16)
            elif mode == 'AFFECTED MEMORY':
                # "0x20070000: 0xAB"
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    memory[int(parts[0], 16)] = int(parts[1], 16)
            elif mode == 'ERROR MESSAGE':
                error_msg += line + '\n'
        return status, disasm, registers, memory, error_msg.strip()


# ===========================================================================
# Assemble tests
# ===========================================================================

class AssembleTestCase(unittest.TestCase):
    """Tests for the ASSEMBLE command. Each test manages its own connection."""

    @classmethod
    def setUpClass(cls):
        if shutil.which('arm-none-eabi-gcc') is None:
            raise unittest.SkipTest("arm-none-eabi-gcc not found in PATH")

    def setUp(self):
        self.mySocket: MySocket = MySocket()
        try:
            self.mySocket.connectTo(PORT)
        except ConnectionRefusedError:
            self.mySocket.closeConnection()
            self.skipTest("Server not running on port {}".format(PORT))
        self.mySocket.setConnTimeout(2.0)  # pyright: ignore[reportOptionalMemberAccess]

    def tearDown(self):
        self.mySocket.closeConnection()

    def _set_path(self):
        self.mySocket.sendLine("CONFIG PATH {}".format(TEST_DIR))
        self.assertEqual(self.mySocket.receiveLine(), OK)

    def test_assemble_success(self):
        """ASSEMBLE add.s should return SUCCESS."""
        self._set_path()
        self.mySocket.sendLine("ASSEMBLE add.s")
        self.assertEqual(self.mySocket.receiveLine(), 'SUCCESS')

    def test_assemble_nonexistent_file(self):
        """ASSEMBLE on a missing .s file should return a file-not-found error."""
        self._set_path()
        self.mySocket.sendLine("ASSEMBLE nonexistent.s")
        response = self.mySocket.receiveLine()
        self.assertNotEqual(response, 'SUCCESS', "Expected an error for missing file")

    def test_assemble_enables_reset_registers(self):
        """After ASSEMBLE, RESET REGISTERS should succeed (processor is initialised)."""
        self._set_path()
        self.mySocket.sendLine("ASSEMBLE add.s")
        self.assertEqual(self.mySocket.receiveLine(), 'SUCCESS')
        self.mySocket.sendLine("RESET REGISTERS")
        self.assertEqual(self.mySocket.receiveLine(), OK)


# ===========================================================================
# Disassemble tests
# ===========================================================================

class DisassembleTestCase(_BaseSimulatorTest):
    """Tests for the DISASSEMBLE command (requires an assembled program)."""

    def test_disassemble_returns_lines_and_eof(self):
        """DISASSEMBLE should return at least one line followed by EOF."""
        self.mySocket.sendLine("DISASSEMBLE 0x{:08X} 4".format(ORIG_CODE))
        lines = self._receive_till_eof()
        self.assertGreater(len(lines), 0, "Expected at least one disassembly line")

    def test_disassemble_line_format(self):
        """Each disassembly line should start with '[0x'."""
        self.mySocket.sendLine("DISASSEMBLE 0x{:08X} 4".format(ORIG_CODE))
        for line in self._receive_till_eof():
            self.assertTrue(line.startswith('[0x'),
                            "Expected '[0x...' format, got: {}".format(line))

    def test_disassemble_starts_at_orig_code(self):
        """First disassembly line should reference ORIG_CODE."""
        self.mySocket.sendLine("DISASSEMBLE 0x{:08X} 4".format(ORIG_CODE))
        lines = self._receive_till_eof()
        self.assertTrue(lines[0].startswith('[0x{:08X}]'.format(ORIG_CODE)),
                        "First line should reference 0x{:08X}, got: {}".format(ORIG_CODE, lines[0]))

    def test_disassemble_includes_source_info(self):
        """Disassembly lines for add.s should include '; <lineno> <source>' annotations."""
        self.mySocket.sendLine("DISASSEMBLE 0x{:08X} 4".format(ORIG_CODE))
        lines = self._receive_till_eof()
        has_source = any(';' in line for line in lines)
        self.assertTrue(has_source,
                        "Expected source annotations (';') in disassembly output.\n"
                        "Lines: {}".format(lines))


# ===========================================================================
# Execute tests
# ===========================================================================

class ExecuteTestCase(_BaseSimulatorTest):
    """Tests for the EXECUTE command (requires an assembled program).

    add.s program:
        mov r0, #5   @ step 1 → r0 = 5
        mov r1, #4   @ step 2 → r1 = 4
        add r2,r1,r0 @ step 3 → r2 = 9
        wfi          @ end of program
    """

    def test_execute_step_returns_success(self):
        """EXECUTE STEP on a normal instruction should return SUCCESS."""
        self.mySocket.sendLine("EXECUTE STEP")
        status, *_ = self._parse_execute_response()
        self.assertEqual(status, 'SUCCESS')

    def test_execute_step_sets_r0(self):
        """First EXECUTE STEP (mov r0, #5) should report r0 = 5."""
        self.mySocket.sendLine("EXECUTE STEP")
        status, _, registers, _, _ = self._parse_execute_response()
        self.assertEqual(status, 'SUCCESS')
        self.assertEqual(registers.get('r0'), 5)

    def test_execute_step_disasm_at_orig_code(self):
        """First EXECUTE STEP disassembly line should reference ORIG_CODE."""
        self.mySocket.sendLine("EXECUTE STEP")
        _, disasm, _, _, _ = self._parse_execute_response()
        self.assertTrue(disasm.startswith('[0x{:08X}]'.format(ORIG_CODE)),
                        "Expected disasm at 0x{:08X}, got: {}".format(ORIG_CODE, disasm))

    def test_execute_step_has_affected_registers(self):
        """EXECUTE STEP response must always include at least the flags register (r16)."""
        self.mySocket.sendLine("EXECUTE STEP")
        _, _, registers, _, _ = self._parse_execute_response()
        self.assertIn('r16', registers, "r16 (flags) must always be in AFFECTED REGISTERS")

    def test_execute_three_steps_register_values(self):
        """After three EXECUTE STEPs, r0=5, r1=4, r2=9."""
        for _ in range(3):
            self.mySocket.sendLine("EXECUTE STEP")
            status, _, _, _, _ = self._parse_execute_response()
            self.assertEqual(status, 'SUCCESS')
        for reg, expected in (('r0', 5), ('r1', 4), ('r2', 9)):
            self.mySocket.sendLine("SHOW REGISTER {}".format(reg))
            line = self.mySocket.receiveLine()
            value = int(line.split(': ')[1], 16)
            self.assertEqual(value, expected,
                             "{} should be {} after three steps".format(reg, expected))

    def test_execute_step_at_end_returns_error(self):
        """EXECUTE STEP when PC is at wfi should return ERROR."""
        for _ in range(3):  # advance past mov/mov/add to wfi
            self.mySocket.sendLine("EXECUTE STEP")
            self._receive_till_eof()
        self.mySocket.sendLine("EXECUTE STEP")
        status, _, _, _, _ = self._parse_execute_response()
        self.assertEqual(status, 'ERROR')

    def test_execute_all_ends_at_wfi(self):
        """EXECUTE ALL should stop at the wfi end-of-program instruction."""
        self.mySocket.sendLine("EXECUTE ALL")
        status, _, registers, _, _ = self._parse_execute_response()
        self.assertEqual(status, 'END OF PROGRAM')
        self.assertEqual(registers.get('r0'), 5)
        self.assertEqual(registers.get('r1'), 4)
        self.assertEqual(registers.get('r2'), 9)

    def test_execute_subroutine_on_non_call(self):
        """EXECUTE SUBROUTINE on a non-BLX instruction should return ERROR
        with 'No es subrutina' and still execute the instruction."""
        self.mySocket.sendLine("EXECUTE SUBROUTINE")
        status, _, registers, _, error_msg = self._parse_execute_response()
        self.assertEqual(status, 'ERROR')
        self.assertIn('No es subrutina', error_msg)
        self.assertEqual(registers.get('r0'), 5, "Instruction should still have been executed")


def suite():
    """
    Used to manually define the suite of tests that should be executed.
    """
    # To check specific tests, change manual_suite to True and add as addTest
    # lines are required.
    manual_suite = True
    if manual_suite:
        suite_ = unittest.TestSuite()
        suite_.addTest(CommunicationTestCase('test_show_version'))
        suite_.addTest(CommunicationTestCase('test_show_register_r0'))
        suite_.addTest(CommunicationTestCase('test_set_register_r1'))

        suite_.addTest(CommunicationTestCase('test_reset_registers'))
        suite_.addTest(CommunicationTestCase('test_show_memory_byte'))
        suite_.addTest(CommunicationTestCase('test_show_memory_half'))
        suite_.addTest(CommunicationTestCase('test_show_memory_word'))
        suite_.addTest(CommunicationTestCase('test_endianess'))
        suite_.addTest(CommunicationTestCase('test_reset_memory'))

        suite_.addTest(CommunicationTestCase('test_dump_registers'))
        suite_.addTest(CommunicationTestCase('test_set_memory_byte'))
        suite_.addTest(CommunicationTestCase('test_set_memory_half'))
        suite_.addTest(CommunicationTestCase('test_set_memory_word'))

        suite_.addTest(CommunicationTestCase('test_dump_memory'))
        suite_.addTest(CommunicationTestCase('test_breakpoints'))

        # Assemble tests
        suite_.addTest(AssembleTestCase('test_assemble_success'))
        suite_.addTest(AssembleTestCase('test_assemble_nonexistent_file'))
        suite_.addTest(AssembleTestCase('test_assemble_enables_reset_registers'))

        # Disassemble tests (require assembled program)
        suite_.addTest(DisassembleTestCase('test_disassemble_returns_lines_and_eof'))
        suite_.addTest(DisassembleTestCase('test_disassemble_line_format'))
        suite_.addTest(DisassembleTestCase('test_disassemble_starts_at_orig_code'))
        suite_.addTest(DisassembleTestCase('test_disassemble_includes_source_info'))

        # Execute tests (require assembled program)
        suite_.addTest(ExecuteTestCase('test_execute_step_returns_success'))
        suite_.addTest(ExecuteTestCase('test_execute_step_sets_r0'))
        suite_.addTest(ExecuteTestCase('test_execute_step_disasm_at_orig_code'))
        suite_.addTest(ExecuteTestCase('test_execute_step_has_affected_registers'))
        suite_.addTest(ExecuteTestCase('test_execute_three_steps_register_values'))
        suite_.addTest(ExecuteTestCase('test_execute_step_at_end_returns_error'))
        suite_.addTest(ExecuteTestCase('test_execute_all_ends_at_wfi'))
        suite_.addTest(ExecuteTestCase('test_execute_subroutine_on_non_call'))

        return suite_
    else:
        return None


if __name__ == '__main__':
    getopts()
    s = suite()
    if s:
        unittest.TextTestRunner().run(s)
    else:
        unittest.main()
