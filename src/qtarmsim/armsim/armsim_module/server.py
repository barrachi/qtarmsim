# -*- coding: utf-8 -*-
# ARM Thumb-II simulator — in-process command handler.
# Derived from armsim_python/server.py; socket/subprocess server code removed.

import os
import subprocess

from . import read_elf as _elf_mod
from . import thumb2_defs as T
from .coder import Coder
from .core import Core
from .instruction import Instruction
from .memory_block import MemoryBlock
from .read_elf import read_elf, ORIG_CODE, END_DATA

ORIG_DISP = 0x20080000
SIZE_DISP = 0x400

ERRORS = {
    'orden':      "Orden no reconocida\r\n",
    'args':       "Argumentos erróneos\r\n",
    'sistema':    "Error del sistema\r\n",
    'rango':      "Fuera de rango\r\n",
    'vacio':      "No hay datos\r\n",
    'noexec':     "Instrución indefinida o impredecible\r\n",
    'call':       "No es subrutina\r\nSe ejecuta STEP\r\n",
    'end':        "Se intenta ejecutar al final del programa\r\n",
    'breakpoint': "Se ejecuta desde dirección de breakpoint\r\nEl breakpoint se ignora\r\n",
    'nomem':      "Se intenta ejecutar fuera de la memoria\r\n",
    'path':       "El directorio no existe o no es correcto\r\n",
    'exe':        "El archivo no existe o no es ejecutable\r\n",
    'file_s':     "El archivo .s no existe\r\n",
    'errnoalign': "Acceso no alineado a la dirección",
    'errnoblock': "Memoria inexistente en dirección",
}


def flags_to_reg(flags: dict) -> int:
    reg = 0
    if flags['n'] == 1: reg += 0x80000000
    if flags['z'] == 1: reg += 0x40000000
    if flags['c'] == 1: reg += 0x20000000
    if flags['v'] == 1: reg += 0x10000000
    return reg


def reg_to_flags(reg: int) -> dict:
    return {
        'n': 1 if reg & 0x80000000 else 0,
        'z': 1 if reg & 0x40000000 else 0,
        'c': 1 if reg & 0x20000000 else 0,
        'v': 1 if reg & 0x10000000 else 0,
    }


def _get_section(line: str | None) -> int:
    if not line:
        return 0
    secs = ['.text', '.data', '.bss', '.rodata']
    parts = line.split()
    if not parts:
        return 0
    if parts[0] == '.section' and len(parts) > 1:
        try:
            return secs.index(parts[1]) + 1
        except ValueError:
            return 0
    try:
        return secs.index(parts[0]) + 1
    except ValueError:
        return 0


def gen_source(name: str) -> dict:
    source: dict = {}
    intext = False
    with open(name, encoding='utf-8', errors='replace') as f:
        for raw in f:
            line = raw.rstrip('\n')
            try:
                line_number = int(line[0:4])
            except ValueError:
                line_number = 0
            if line_number != 0:
                try:
                    dir_rel = int(line[5:9], 16)
                except ValueError:
                    dir_rel = 0
                data_part = line[10:18].lstrip()
                text = line[19:].replace('\t', ' ').lstrip() if len(line) > 19 else None
                if intext:
                    if data_part:
                        if text:
                            source[dir_rel] = [text, line_number]
                    elif _get_section(text) > 1:
                        intext = False
                elif _get_section(text) == 1:
                    intext = True
    return source


class MainServer:
    def __init__(self, procesador: Core | None, port: int):
        self.proc: Core | None = procesador
        self.breakpoints: list = []
        self.coder = Coder()
        self._port = port
        self._source: dict = {}
        self._compiler = 'arm-none-eabi-gcc'
        self._args = '-mcpu=cortex-m1 -mthumb -c'
        self._path = './'
        self._firm_table: dict | None = None
        self._firmware_block = None
        self._exit = False

    def _gen_disassemble(self, addr: int) -> tuple[str, Instruction] | None:
        sdir = addr
        res  = "[0x%08X] " % addr
        if self.proc is None:
            return None
        word  = self.proc.memory_half(addr)
        word2 = self.proc.memory_half(addr + 2)
        if isinstance(word, str) or isinstance(word2, str):
            return None
        res += "0x%04X " % word
        inst = self.coder.decode([word, word2], addr)
        if inst.size == 2:
            res += "0x%04X " % word2
        if inst.kind() in ('und', 'unp'):
            res += 'NOT AN INSTRUCTION'
        else:
            res += inst.to_s()
            src = self._source.get(sdir - ORIG_CODE)
            if src:
                res += " ; %04d " % src[1] + src[0]
        return (res, inst)

    # ── Command handlers ────────────────────────────────────────────────────

    def _cmd_show_version(self, _tokens):
        return "V 1.8\r\n(c) 2014-20 Germán Fabregat\r\nATC - UJI\r\nEOF\r\n"

    def _cmd_show_register(self, tokens):
        if self.proc is None:
            return ERRORS['sistema']
        rn = tokens[0]
        if rn > 16:
            return ERRORS['rango']
        if rn == 16:
            return "r16: 0x%08X\r\n" % flags_to_reg(self.proc.flags())
        return "r%d: 0x%08X\r\n" % (rn, self.proc.reg(rn))

    def _cmd_show_memory(self, tokens):
        if self.proc is None:
            return ERRORS['sistema']
        kind, addr = tokens[0], tokens[2]
        if kind == 'BYTE':
            return "0x%08X: 0x%02X\r\n" % (addr, self.proc.memory_byte(addr))
        if kind == 'HALF':
            return "0x%08X: 0x%04X\r\n" % (addr, self.proc.memory_half(addr))
        if kind == 'WORD':
            return "0x%08X: 0x%08X\r\n" % (addr, self.proc.memory_word(addr))
        return ERRORS['args']

    def _cmd_show_breakpoints(self, _tokens):
        return ''.join("0x%08X\r\n" % b for b in self.breakpoints) + "EOF\r\n"

    def _cmd_dump_registers(self, _tokens):
        if self.proc is None:
            return ERRORS['sistema']
        res = ''.join("r%d: 0x%08X\r\n" % (i, self.proc.reg(i)) for i in range(16))
        return res + "r16: 0x%08X\r\n" % flags_to_reg(self.proc.flags())

    def _cmd_dump_memory(self, tokens):
        if self.proc is None:
            return ERRORS['sistema']
        addr, nbytes = tokens[0], tokens[1]
        res = ''
        for _ in range(nbytes):
            b = self.proc.memory_byte(addr)
            if b is None:
                break
            res += "0x%08X: 0x%02X\r\n" % (addr, b)
            addr += 1
        return res + "EOF\r\n"

    def _cmd_reset_registers(self, _tokens):
        if self.proc is None:
            return ERRORS['sistema']
        estado = T.reset()
        regs = []
        for i, v in enumerate(estado['usr_regs']):
            regs.extend([i, v])
        estado['usr_regs'] = regs
        self.proc.update(estado)
        return "OK\r\n"

    def _cmd_reset_memory(self, _tokens):
        if self.proc is None:
            return ERRORS['sistema']
        self.proc.memory().reset()
        return "OK\r\n"

    def _cmd_clear_breakpoints(self, _tokens):
        self.breakpoints.clear()
        return "OK\r\n"

    def _cmd_clear_breakpoint(self, tokens):
        addr = tokens[1]
        if addr in self.breakpoints:
            self.breakpoints.remove(addr)
        return "OK\r\n"

    def _cmd_set_register(self, tokens):
        if self.proc is None:
            return ERRORS['sistema']
        rn, val = tokens[0], tokens[2]
        if rn > 16:
            return ERRORS['rango']
        if rn == 16:
            self.proc.update({'flags': reg_to_flags(val)})
        else:
            self.proc.update({'usr_regs': [rn, val]})
        return "OK\r\n"

    def _cmd_set_memory(self, tokens):
        if self.proc is None:
            return ERRORS['sistema']
        kind, addr, val = tokens[0], tokens[2], tokens[4]
        if kind == 'BYTE':
            self.proc.memory().access('wb', addr, val)
        elif kind == 'HALF':
            self.proc.memory().access('wh', addr, val)
        elif kind == 'WORD':
            self.proc.memory().access('ww', addr, val)
        else:
            return ERRORS['args']
        return "OK\r\n"

    def _cmd_set_breakpoint(self, tokens):
        addr = tokens[1]
        if addr not in self.breakpoints:
            self.breakpoints.append(addr)
        self.breakpoints.sort()
        return "OK\r\n"

    def _cmd_disassemble(self, tokens):
        if self.proc is None:
            return ERRORS['sistema']
        addr, ninst = tokens[0], tokens[1]
        res = ''
        for _ in range(ninst):
            pair = self._gen_disassemble(addr)
            if pair is None:
                break
            res += pair[0] + "\r\n"
            addr += 2
            if pair[1].size == 2:
                addr += 2
        return res + "EOF\r\n"

    def _cmd_execute(self, tokens):
        if self.proc is None:
            return ERRORS['sistema']

        kinds_noexec = ['und', 'unp']
        kinds_end    = ['wfe', 'wfi']
        kinds_subr   = ['blx']

        regs: list = []
        mem:  list = []
        res: str | None = None
        terror: str | None = None

        pc = self.proc.reg(T.PC)
        pair = self._gen_disassemble(pc)
        if pair is None:
            return "ERROR\r\n" + ERRORS['nomem'] + "EOF\r\n"

        mode = tokens[0]
        sigue_fn = None

        if mode == 'STEP':
            sigue_fn = lambda: False
        elif mode == 'SUBROUTINE':
            if pair[1].kind() not in kinds_subr:
                sigue_fn = lambda: False
                terror = ERRORS['call']
        elif mode == 'ALL':
            sigue_fn = lambda: True
        else:
            return ERRORS['args']

        if pair[1].kind() in kinds_noexec:
            return ("ERROR\r\n" + pair[0] + "\r\n" +
                    "ERROR MESSAGE\r\n" + ERRORS['noexec'] + "EOF\r\n")
        if pair[1].kind() in kinds_end:
            return ("ERROR\r\n" + pair[0] + "\r\n" +
                    "ERROR MESSAGE\r\n" + ERRORS['end'] + "EOF\r\n")
        if pc in self.breakpoints:
            terror = ERRORS['breakpoint']

        mod    = self.proc.execute(pair[1])
        nregs  = len(mod.get('usr_regs', [])) // 2
        nmem   = len(mod['memory'][1]) if mod.get('memory') else 0
        nerror = mod.get('error')

        if nregs > 0:
            for ind in range(nregs):
                r = mod['usr_regs'][2 * ind]
                regs.append(r)
                if sigue_fn is None and r == T.LR:
                    pcold = mod['usr_regs'][2 * ind + 1]
                    def _make_sigue(expected_ret):
                        return lambda: pc != expected_ret
                    sigue_fn = _make_sigue(pcold)
            regs = sorted(set(regs))

        if nmem > 0:
            bytes_count = {'wb': 0, 'wh': 1, 'ww': 3}.get(mod['memory'][0], 0)
            for par in mod['memory'][1]:
                for i in range(bytes_count + 1):
                    mem.append(par[0] + i)
            mem = sorted(set(mem))

        if nerror is not None:
            sigue_fn = lambda: False
            terror = "%s 0x%08X\r\n" % (ERRORS.get(nerror[0], nerror[0]), nerror[1])

        if sigue_fn is None:
            sigue_fn = lambda: False

        pc = self.proc.reg(T.PC)

        while sigue_fn():
            pair = self._gen_disassemble(pc)
            if pair is None:
                terror = ERRORS['nomem']
                break
            if pair[1].kind() in kinds_noexec:
                res = "ERROR\r\n"
                terror = ERRORS['noexec']
                break
            if pair[1].kind() in kinds_end:
                res = "END OF PROGRAM\r\n"
                break
            if pc in self.breakpoints:
                res = "BREAKPOINT REACHED\r\n"
                break
            mod    = self.proc.execute(pair[1])
            pc     = self.proc.reg(T.PC)
            nregs  = len(mod.get('usr_regs', [])) // 2
            nmem   = len(mod['memory'][1]) if mod.get('memory') else 0
            nerror = mod.get('error')
            if nregs > 0:
                for ind in range(nregs):
                    regs.append(mod['usr_regs'][2 * ind])
                regs = sorted(set(regs))
            if nmem > 0:
                bytes_count = {'wb': 0, 'wh': 1, 'ww': 3}.get(mod['memory'][0], 0)
                for par in mod['memory'][1]:
                    for i in range(bytes_count + 1):
                        mem.append(par[0] + i)
                mem = sorted(set(mem))
            if nerror is not None:
                terror = "%s 0x%08X\r\n" % (ERRORS.get(nerror[0], nerror[0]), nerror[1])
                break

        if res is None:
            res = "SUCCESS\r\n" if terror is None else "ERROR\r\n"

        if pair is not None:
            res += pair[0] + "\r\n"
        res += "AFFECTED REGISTERS\r\n"
        for nreg in regs:
            res += "r%d: 0x%08X\r\n" % (nreg, self.proc.reg(nreg))
        res += "r16: 0x%08X\r\n" % flags_to_reg(self.proc.flags())
        if mem:
            res += "AFFECTED MEMORY\r\n"
            for pos in mem:
                res += "0x%08X: 0x%02X\r\n" % (pos, self.proc.memory_byte(pos))
        if terror:
            res += "ERROR MESSAGE\r\n" + terror
        res += "EOF\r\n"
        return res

    def _cmd_config_compiler(self, tokens):
        self._compiler = tokens[0]
        return "OK\r\n"

    def _cmd_config_args(self, tokens):
        self._args = tokens[0]
        return "OK\r\n"

    def _cmd_config_path(self, tokens):
        self._path = tokens[0]
        return "OK\r\n"

    def _cmd_config_labels(self, tokens):
        if tokens[0] == 'TRUE':
            T._use_symbols = True
            return "OK\r\n"
        if tokens[0] == 'FALSE':
            T._use_symbols = False
            return "OK\r\n"
        return ERRORS['args']

    def _cmd_sysinfo_memory(self, _tokens):
        if self.proc is None:
            return ERRORS['sistema']
        return str(self.proc.memory()) + "EOF\r\n"

    def _cmd_assemble(self, tokens):
        filename = tokens[0]
        base = os.path.splitext(filename)[0]
        old_dir = os.getcwd()
        os.chdir(self._path)
        res = ''
        try:
            lst_file = base + '.lst'
            err_file = base + '.err'
            obj_file = base + '.o'
            cmd = ('"' + self._compiler + '" ' + self._args +
                   ' -Wa,-alcd -o ' + obj_file + ' ' + base + '.s')
            proc_result = subprocess.run(
                cmd, shell=True,
                stdout=open(lst_file, 'w'),
                stderr=open(err_file, 'w'),
            )
            if proc_result.returncode == 0:
                blocks = read_elf(obj_file, firm_table=self._firm_table)
                warnings = list(_elf_mod._last_warnings)
                procesador = Core(T.ARCH, blocks[0])
                procesador.memory().add_block(blocks[1])
                procesador.memory().symbol_table = blocks[2]
                disp = MemoryBlock(ORIG_DISP, SIZE_DISP, 'ram_le', 32, 'Display')
                disp.fill_from_val()
                procesador.memory().add_block(disp)
                if self._firmware_block is not None:
                    procesador.memory().add_block(self._firmware_block)
                T._symbol_table = blocks[2]
                dir_pc = blocks[2].get('main', ORIG_CODE)
                procesador.update({'usr_regs': [T.PC, dir_pc, T.SP, END_DATA - 128]})
                self.proc = procesador
                self._source = gen_source(lst_file)
                if not warnings:
                    res = "SUCCESS\r\n"
                else:
                    res = "ERROR\r\n"
                    for w in warnings:
                        res += w + "\r\n"
                    res += "EOF\r\n"
            else:
                res = "ERROR\r\n"
                try:
                    with open(err_file) as ef:
                        for line in ef:
                            res += line.rstrip('\n') + "\r\n"
                except OSError:
                    pass
                res += "EOF\r\n"
            for f in (err_file, lst_file):
                try:
                    os.remove(f)
                except OSError:
                    pass
        finally:
            os.chdir(old_dir)
        return res

    def _cmd_exit(self, _tokens):
        self._exit = True
        return "OK\r\n"

    @property
    def _dispatch(self):
        return {
            'SHOW': {
                'VERSION':     (self._cmd_show_version,    []),
                'REGISTER':    (self._cmd_show_register,   ['regname']),
                'MEMORY':      (self._cmd_show_memory,     ['keyword', 'AT', 'address']),
                'BREAKPOINTS': (self._cmd_show_breakpoints,[]),
            },
            'DUMP': {
                'REGISTERS': (self._cmd_dump_registers, []),
                'MEMORY':    (self._cmd_dump_memory,    ['address', 'nbytes']),
            },
            'RESET': {
                'REGISTERS': (self._cmd_reset_registers, []),
                'MEMORY':    (self._cmd_reset_memory,    []),
            },
            'CLEAR': {
                'BREAKPOINTS': (self._cmd_clear_breakpoints, []),
                'BREAKPOINT':  (self._cmd_clear_breakpoint,  ['AT', 'address']),
            },
            'SET': {
                'REGISTER':  (self._cmd_set_register, ['regname', 'WITH', 'hexvalue']),
                'MEMORY':    (self._cmd_set_memory,   ['keyword', 'AT', 'address', 'WITH', 'hexvalue']),
                'BREAKPOINT':(self._cmd_set_breakpoint, ['AT', 'address']),
            },
            'DISASSEMBLE': (self._cmd_disassemble, ['address', 'ninst']),
            'EXECUTE':     (self._cmd_execute,     ['keyword']),
            'ASSEMBLE':    (self._cmd_assemble,    ['file_s']),
            'CONFIG': {
                'COMPILER':  (self._cmd_config_compiler, ['exe']),
                'ARGS':      (self._cmd_config_args,     ['cad']),
                'PATH':      (self._cmd_config_path,     ['path']),
                'USELABELS': (self._cmd_config_labels,   ['keyword']),
            },
            'SYSINFO': {
                'MEMORY': (self._cmd_sysinfo_memory, []),
            },
            'EXIT': (self._cmd_exit, []),
        }

    def process(self, request: str) -> str:
        tokens = request.split()
        if not tokens:
            return ERRORS['orden']

        table = self._dispatch
        pos = 0

        while pos < len(tokens):
            key = tokens[pos]
            pos += 1
            entry = table.get(key)
            if entry is None:
                return ERRORS['orden']
            if isinstance(entry, dict):
                table = entry
                continue
            handler, arg_spec = entry
            remaining = tokens[pos:]

            last_spec = arg_spec[-1] if arg_spec else None
            flexible = last_spec in ('cad', 'exe', 'path')
            if flexible:
                if len(remaining) < len(arg_spec):
                    return ERRORS['args']
            else:
                if len(remaining) != len(arg_spec):
                    return ERRORS['args']

            parsed: list = []
            for i, spec in enumerate(arg_spec):
                tok = remaining[i]
                if spec in ('AT', 'WITH'):
                    if tok != spec:
                        return ERRORS['args']
                    parsed.append(1)
                elif spec == 'regname':
                    if not tok.startswith('r'):
                        return ERRORS['args']
                    try:
                        parsed.append(int(tok[1:]))
                    except ValueError:
                        return ERRORS['args']
                elif spec in ('hexvalue', 'address'):
                    try:
                        parsed.append(int(tok, 16))
                    except ValueError:
                        return ERRORS['args']
                elif spec in ('nbytes', 'ninst'):
                    try:
                        parsed.append(int(tok))
                    except ValueError:
                        return ERRORS['args']
                elif spec == 'file_s':
                    base = os.path.splitext(tok)[0]
                    if not os.path.isfile(self._path + base + '.s'):
                        return ERRORS['file_s']
                    parsed.append(tok)
                elif spec in ('cad', 'exe', 'path'):
                    cad = ' '.join(remaining[i:])
                    if spec == 'path':
                        cad = cad.replace('\\', '/')
                        if not os.path.isdir(cad):
                            return ERRORS['path']
                        if not cad.endswith('/'):
                            cad += '/'
                    elif spec == 'exe':
                        cad = cad.replace('\\', '/')
                        if not os.access(cad, os.X_OK):
                            return ERRORS['exe']
                    parsed.append(cad)
                else:
                    parsed.append(tok)

            return handler(parsed)

        return ERRORS['orden']
