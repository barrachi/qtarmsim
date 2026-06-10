# -*- coding: utf-8 -*-
# ARM Thumb-II ISA definitions: decoding tables, disassembly, and execution.
# Translated from the original Ruby thumbII_Defs.rb module.

# ── Architecture constants ──────────────────────────────────────────────────
ARCH = 'Instrucciones Thumb de 16 bits'
PC   = 15
LR   = 14
SP   = 13
APSR = 16

# ── Instruction set table ───────────────────────────────────────────────────
# Format: type_id -> [mnemonic, operation_id, [operand_types], [masks], num_halfs]
SET = {
    'lslit1':   ['lsl', 'lsl', ['r3', 'r3', 'imm5'],      [0x0007, 0x0038, 0x07C0], 1],
    'lsrit1':   ['lsr', 'lsr', ['r3', 'r3', 'imm5'],      [0x0007, 0x0038, 0x07C0], 1],
    'asrit1':   ['asr', 'asr', ['r3', 'r3', 'imm5'],      [0x0007, 0x0038, 0x07C0], 1],
    'movit1':   ['mov', 'mov', ['r3', 'imm8'],             [0x0700, 0x00FF], 1],
    'cmpit1':   ['cmp', 'add', ['r3', 'imm8'],             [0x0700, 0x00FF], 1],
    'addit2':   ['add', 'add', ['r3', 'imm8'],             [0x0700, 0x00FF], 1],
    'subit2':   ['sub', 'add', ['r3', 'imm8'],             [0x0700, 0x00FF], 1],
    'addrt1':   ['add', 'add', ['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'subrt1':   ['sub', 'add', ['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'addit1':   ['add', 'add', ['r3', 'r3', 'imm3'],       [0x0007, 0x0038, 0x01C0], 1],
    'subit1':   ['sub', 'add', ['r3', 'r3', 'imm3'],       [0x0007, 0x0038, 0x01C0], 1],
    'andrt1':   ['and', 'and', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'eorrt1':   ['eor', 'eor', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'lslrt1':   ['lsl', 'lsl', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'lsrrt1':   ['lsr', 'lsr', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'asrrt1':   ['asr', 'asr', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'adcrt1':   ['adc', 'add', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'sbcrt1':   ['sbc', 'add', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'rorrt1':   ['ror', 'ror', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'tstrt1':   ['tst', 'and', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'rsbrt1':   ['rsb', 'add', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'cmprt1':   ['cmp', 'add', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'cmnrt1':   ['cmn', 'add', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'orrrt1':   ['orr', 'orr', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'mult1':    ['mul', 'mul', ['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x0007], 1],
    'bicrt1':   ['bic', 'and', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'mvnrt1':   ['mvn', 'mov', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'addrt2':   ['add', 'add', ['r4d', 'r4'],              [0x0087, 0x0078], 1],
    'unpred':   ['unp', 'unp', [],                         [], 1],
    'cmprt2':   ['cmp', 'add', ['r4d', 'r4'],              [0x0087, 0x0078], 1],
    'movrt1':   ['mov', 'mov', ['r4d', 'r4'],              [0x0087, 0x0078], 1],
    'bxt1':     ['bx',  'bx',  ['r4'],                     [0x0078], 1],
    'blxt1':    ['blx', 'blx', ['r4'],                     [0x0078], 1],
    'ldrlt1':   ['ldr', 'ldr', ['r3', 'label8'],           [0x0700, 0x00FF], 1],
    'strrt1':   ['str', 'str', ['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'strhrt1':  ['strh','strh',['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'strbrt1':  ['strb','strb',['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'ldrsbrt1': ['ldrsb','ldr',['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'ldrrt1':   ['ldr', 'ldr', ['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'ldrhrt1':  ['ldrh','ldr', ['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'ldrbrt1':  ['ldrb','ldr', ['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'ldrshrt1': ['ldrsh','ldr',['r3', 'r3', 'r3'],         [0x0007, 0x0038, 0x01C0], 1],
    'strit1':   ['str', 'str', ['r3', 'r3', 'imm5x4'],     [0x0007, 0x0038, 0x07C0], 1],
    'ldrit1':   ['ldr', 'ldr', ['r3', 'r3', 'imm5x4'],     [0x0007, 0x0038, 0x07C0], 1],
    'strbit1':  ['strb','strb',['r3', 'r3', 'imm5'],       [0x0007, 0x0038, 0x07C0], 1],
    'ldrbit1':  ['ldrb','ldr', ['r3', 'r3', 'imm5'],       [0x0007, 0x0038, 0x07C0], 1],
    'strhit1':  ['strh','strh',['r3', 'r3', 'imm5x2'],     [0x0007, 0x0038, 0x07C0], 1],
    'ldrhit1':  ['ldrh','ldr', ['r3', 'r3', 'imm5x2'],     [0x0007, 0x0038, 0x07C0], 1],
    'strit2':   ['str', 'str', ['r3', 'imm8x4'],           [0x0700, 0x00FF], 1],
    'ldrit2':   ['ldr', 'ldr', ['r3', 'imm8x4'],           [0x0700, 0x00FF], 1],
    'adrit1':   ['adr', 'adr', ['r3', 'label8'],           [0x0700, 0x00FF], 1],
    'addspit1': ['add', 'add', ['r3', 'imm8x4'],           [0x0700, 0x00FF], 1],
    'addspit2': ['add', 'add', ['imm7x4'],                 [0x007F], 1],
    'subspit1': ['sub', 'add', ['imm7x4'],                 [0x007F], 1],
    'cbzt1':    ['cbz', 'cbz', ['r3', 'label6d'],          [0x0007, 0x02F8], 1],
    'sxtht1':   ['sxth','sxth',['r3', 'r3'],               [0x0007, 0x0038], 1],
    'sxtbt1':   ['sxtb','sxtb',['r3', 'r3'],               [0x0007, 0x0038], 1],
    'uxtht1':   ['uxth','uxth',['r3', 'r3'],               [0x0007, 0x0038], 1],
    'uxtbt1':   ['uxtb','uxtb',['r3', 'r3'],               [0x0007, 0x0038], 1],
    'pusht1':   ['push','push',['rl9'],                    [0x01FF], 1],
    'cpst1':    ['cps', 'cps', ['b1', 'b2'],               [0x0010, 0x0003], 1],
    'cbnzt1':   ['cbnz','cbnz',['r3', 'label6d'],          [0x0007, 0x02F8], 1],
    'revt1':    ['rev', 'rev', ['r3', 'r3'],               [0x0007, 0x0038], 1],
    'rev16t1':  ['rev16','rev16',['r3', 'r3'],             [0x0007, 0x0038], 1],
    'revsht1':  ['revsh','revsh',['r3', 'r3'],             [0x0007, 0x0038], 1],
    'popt1':    ['pop', 'pop', ['rl9'],                    [0x01FF], 1],
    'bkptt1':   ['bkpt','bkpt',['imm8'],                   [0x00FF], 1],
    'stmt1':    ['stm', 'stm', ['r3', 'rl8'],              [0x0700, 0x00FF], 1],
    'ldmt1':    ['ldm', 'ldm', ['r3', 'rl8'],              [0x0700, 0x00FF], 1],
    'udef':     ['und', 'und', [],                         [], 1],
    'svct1':    ['svc', 'svc', ['imm8'],                   [0x00FF], 1],
    'bt1':      ['b',   'b',   ['cond', 'label8s'],        [0x0F00, 0x00FF], 1],
    'bt2':      ['b',   'b',   ['label11s'],               [0x07FF], 1],
    'nopt1':    ['nop', 'nop', [],                         [], 1],
    'yieldt1':  ['yield','yield',[],                       [], 1],
    'wfet1':    ['wfe', 'wfe', [],                         [], 1],
    'wfit1':    ['wfi', 'wfi', [],                         [], 1],
    'sevt1':    ['sev', 'sev', [],                         [], 1],
    'itt1':     ['it',  'it',  ['imm4', 'cond'],           [0x000F, 0x00F0], 1],
    'blt1':     ['bl',  'blx', ['labeldbl'],               [0x07FF2FFF], 2],
    'bt4':      ['b',   'b',   ['labeldbl'],               [0x07FF2FFF], 2],
    'udef32':   ['und', 'und', [],                         [], 2],
}

# ── Decoding tables ─────────────────────────────────────────────────────────
# Terminal entries:     [pattern, 0, instr_type_id]
# Non-terminal entries: [pattern, num_bits, mask, sublist, num_halfs, ...]

PRINCIPAL = [
    ['000xx', 0, 'lslit1'],
    ['001xx', 0, 'lsrit1'],
    ['010xx', 0, 'asrit1'],
    ['01100', 0, 'addrt1'],
    ['01101', 0, 'subrt1'],
    ['01110', 0, 'addit1'],
    ['01111', 0, 'subit1'],
    ['100xx', 0, 'movit1'],
    ['101xx', 0, 'cmpit1'],
    ['110xx', 0, 'addit2'],
    ['111xx', 0, 'subit2'],
]

ALU = [
    ['0000', 0, 'andrt1'],
    ['0001', 0, 'eorrt1'],
    ['0010', 0, 'lslrt1'],
    ['0011', 0, 'lsrrt1'],
    ['0100', 0, 'asrrt1'],
    ['0101', 0, 'adcrt1'],
    ['0110', 0, 'sbcrt1'],
    ['0111', 0, 'rorrt1'],
    ['1000', 0, 'tstrt1'],
    ['1001', 0, 'rsbrt1'],
    ['1010', 0, 'cmprt1'],
    ['1011', 0, 'cmnrt1'],
    ['1100', 0, 'orrrt1'],
    ['1101', 0, 'mult1'],
    ['1110', 0, 'bicrt1'],
    ['1111', 0, 'mvnrt1'],
]

ESPECIAL = [
    ['00xx', 0, 'addrt2'],
    ['0100', 0, 'unpred'],
    ['01xx', 0, 'cmprt2'],
    ['10xx', 0, 'movrt1'],
    ['110x', 0, 'bxt1'],
    ['111x', 0, 'blxt1'],
]

LDSTRREG = [
    ['000', 0, 'strrt1'],
    ['001', 0, 'strhrt1'],
    ['010', 0, 'strbrt1'],
    ['011', 0, 'ldrsbrt1'],
    ['100', 0, 'ldrrt1'],
    ['101', 0, 'ldrhrt1'],
    ['110', 0, 'ldrbrt1'],
    ['111', 0, 'ldrshrt1'],
]

LDSTRIMM = [
    ['00', 0, 'strit1'],
    ['01', 0, 'ldrit1'],
    ['10', 0, 'strbit1'],
    ['11', 0, 'ldrbit1'],
]

LDSTRMIX = [
    ['00', 0, 'strhit1'],
    ['01', 0, 'ldrhit1'],
    ['10', 0, 'strit2'],
    ['11', 0, 'ldrit2'],
]

HINTS = [
    ['00000000', 0, 'nopt1'],
    ['00010000', 0, 'yieldt1'],
    ['0001xxxx', 0, 'itt1'],
    ['00100000', 0, 'wfet1'],
    ['0010xxxx', 0, 'itt1'],
    ['00110000', 0, 'wfit1'],
    ['0011xxxx', 0, 'itt1'],
    ['01000000', 0, 'sevt1'],
    ['0100xxxx', 0, 'itt1'],
    ['xxxx0000', 0, 'udef'],
    ['xxxxxxxx', 0, 'itt1'],
]

MISC = [
    ['00000xx', 0, 'addspit2'],
    ['00001xx', 0, 'subspit1'],
    ['0001xxx', 0, 'cbzt1'],
    ['001000x', 0, 'sxtht1'],
    ['001001x', 0, 'sxtbt1'],
    ['001010x', 0, 'uxtht1'],
    ['001011x', 0, 'uxtbt1'],
    ['0011xxx', 0, 'cbzt1'],
    ['010xxxx', 0, 'pusht1'],
    ['0110011', 0, 'cpst1'],
    ['1001xxx', 0, 'cbnzt1'],
    ['101000x', 0, 'revt1'],
    ['101001x', 0, 'rev16t1'],
    ['101011x', 0, 'revsht1'],
    ['1011xxx', 0, 'cbnzt1'],
    ['110xxxx', 0, 'popt1'],
    ['1110xxx', 0, 'bkptt1'],
    ['1111xxx', 8, 0x00FF, HINTS, 1],
]

BSVC = [
    ['0xxx', 0, 'bt1'],
    ['10xx', 0, 'bt1'],
    ['110x', 0, 'bt1'],
    ['1110', 0, 'udef32'],
    ['1111', 0, 'svct1'],
]

BMSC32 = [
    ['xxxxxxxxxxx10x1', 0, 'bt4'],
    ['xxxxxxxxxxx11x1', 0, 'blt1'],
]

TH32B10 = [
    ['xxxxxxxxxxx1', 15, 0x07FFF000, BMSC32, 2],
]

GROUPS = [
    ['00xxxx', 5, 0x3E00, PRINCIPAL, 1, 'Principal'],
    ['010000', 4, 0x03C0, ALU,       1, 'Alu'],
    ['010001', 4, 0x03C0, ESPECIAL,  1, 'Especial'],
    ['01001x', 0, 'ldrlt1', 'LDR'],
    ['0101xx', 3, 0x0E00, LDSTRREG, 1, 'Load Store Register'],
    ['011xxx', 2, 0x1800, LDSTRIMM, 1, 'Load Store Immediate'],
    ['100xxx', 2, 0x1800, LDSTRMIX, 1, 'Load Store Mixed'],
    ['10100x', 0, 'adrit1',   'ADR'],
    ['10101x', 0, 'addspit1', 'ADD SP'],
    ['1011xx', 7, 0x0FE0, MISC,     1, 'Miscellaneous'],
    ['11000x', 0, 'stmt1', 'STM'],
    ['11001x', 0, 'ldmt1', 'LDM'],
    ['1101xx', 4, 0x0F00, BSVC,     1, 'B SVC'],
    ['11100x', 0, 'bt2', 'B'],
    ['11110x', 12, 0x07FF8000, TH32B10, 2, '32 bits, bloque 10'],
]

# [None, num_bits, mask, list, num_halfs]
MAINOPC = [None, 6, 0xFC00, GROUPS, 1]

# ── Utility functions ───────────────────────────────────────────────────────
PRIMALIAS = 13  # SP
REGALIAS = ['sp', 'lr', 'pc']


def valor_campo(word: int, mask: int, tipo: str = 'notipo') -> int:
    """Extract bit-field selected by mask, right-justified."""
    salida = word & mask
    m = mask
    while m % 2 == 0:
        salida //= 2
        m //= 2
    if tipo == 'r4d' and salida > 8:
        salida = 8 + (salida & 7)
    return salida


def to_bin(value: int, num_bits: int) -> str:
    """Convert integer to binary string of given width."""
    result = ''
    for _ in range(num_bits):
        result = ('1' if value & 1 else '0') + result
        value >>= 1
    return result


def compara_bin(s1: str, s2: str) -> int:
    """Compare s1 against s2 (which may contain 'x' wildcards).
    Returns 1 if s1 > s2, -1 if s1 < s2, 0 if equal/match."""
    for i, ch in enumerate(s2):
        if ch == 'x':
            continue
        if s1[i] > ch:
            return 1
        if s1[i] < ch:
            return -1
    return 0


def eval_cond(cond: int, flags: dict) -> bool:
    """Evaluate ARM condition code against flags (ARMv7 manual p.209)."""
    toggle = cond & 1
    cond_hi = (cond >> 1) & 7
    if cond_hi == 0:
        res = flags['z'] == 1
    elif cond_hi == 1:
        res = flags['c'] == 1
    elif cond_hi == 2:
        res = flags['n'] == 1
    elif cond_hi == 3:
        res = flags['v'] == 1
    elif cond_hi == 4:
        res = flags['c'] == 1 and flags['z'] == 0
    elif cond_hi == 5:
        res = flags['n'] == flags['v']
    elif cond_hi == 6:
        res = flags['n'] == flags['v'] and flags['z'] == 0
    else:  # 7 - always
        res = True
    if toggle == 1 and cond_hi != 7:
        res = not res
    return res


# ── Disassembly globals ─────────────────────────────────────────────────────
_address: int | None = None
_symbol_table: dict | None = None
_use_symbols: bool = False
_itlist: list | None = None

CONCODES = ['eq', 'ne', 'cs', 'cc', 'mi', 'pl', 'vs', 'vc',
            'hi', 'ls', 'ge', 'lt', 'gt', 'le', 'al', 'al']


def _cond_to_s(n: int) -> str:
    return CONCODES[n]


def _nreg_to_s(n: int) -> str:
    if n < PRIMALIAS:
        return 'r' + str(n)
    return REGALIAS[n - PRIMALIAS]


def _imm_to_s(n: int) -> str:
    return '#' + str(n)


def _immx2_to_s(n: int) -> str:
    return '#' + str(n * 2)


def _immx4_to_s(n: int) -> str:
    return '#' + str(n * 4)


def _label_to_s(n: int) -> str:
    return '#' + str(n * 4)


def _labeld_to_s(n: int) -> str:
    n = 32 + (n & 31) if n > 31 else n
    if _address is not None:
        target = _address + 4 + n * 2
        if _use_symbols and _symbol_table:
            for k, v in _symbol_table.items():
                if v == target:
                    return k
    return 'pc, #' + str(n * 2)


def _label8s_to_s(n: int) -> str:
    n = -(((n ^ 0xFF) + 1)) if n > 127 else n
    if _address is not None:
        target = _address + 4 + n * 2
        if _use_symbols and _symbol_table:
            for k, v in _symbol_table.items():
                if v == target:
                    return k
    return 'pc, #' + str(n * 2)


def _label11s_to_s(n: int) -> str:
    n = -(((n ^ 0x7FF) + 1)) if n > 1023 else n
    if _address is not None:
        target = _address + 4 + n * 2
        if _use_symbols and _symbol_table:
            for k, v in _symbol_table.items():
                if v == target:
                    return k
    return 'pc, #' + str(n * 2)


def _labeldbl_to_s(n: int) -> str:
    imm11 = n & 0x7FF
    imm10 = (n & 0x03FF0000) >> 5
    s = 0 if (n & 0x04000000) == 0 else 1
    j1 = 0 if (n & 0x02000) == 0 else 1
    j2 = 0 if (n & 0x0800) == 0 else 1
    i1 = 1 if s == j1 else 0
    i2 = 1 if s == j2 else 0
    imm3 = (s * 4 + i1 * 2 + i2) << 21
    imm = (imm3 & 0x0E00000) | (imm10 & 0x1FF800) | imm11
    imm = -(((imm ^ 0xEFFFFF) + 1) & 0xEFFFFF) if s == 1 else imm
    if _address is not None:
        target = _address + 4 + imm * 2
        if _use_symbols and _symbol_table:
            for k, v in _symbol_table.items():
                if v == target:
                    return k
    return 'pc, #' + str(imm * 2)


def _rlist9_to_s(n: int) -> str:
    cad = '{'
    state = 0
    hay = 0
    first = 0
    val = n
    for ind in range(8):
        entrada = val & 1
        val >>= 1
        if state == 0:
            if entrada == 1:
                if hay:
                    cad += ', '
                cad += 'r' + str(ind)
                first = ind
                hay = 1
                state = 1
        else:
            if entrada == 0:
                if ind != first + 1:
                    cad += '-r' + str(ind - 1)
                state = 0
    if state == 1 and first < 7:
        cad += '-r7'
    if val & 1:
        if hay:
            cad += ', '
        cad += 'x'
    cad += '}'
    return cad


OPTOS = {
    'r3':       _nreg_to_s,
    'r4':       _nreg_to_s,
    'r4d':      _nreg_to_s,
    'label8':   _label_to_s,
    'label6d':  _labeld_to_s,
    'label8s':  _label8s_to_s,
    'label11s': _label11s_to_s,
    'labeldbl': _labeldbl_to_s,
    'imm5x2':   _immx2_to_s,
    'imm5x4':   _immx4_to_s,
    'imm8x4':   _immx4_to_s,
    'imm3':     _imm_to_s,
    'imm7x4':   _immx4_to_s,
    'imm4':     _imm_to_s,
    'imm5':     _imm_to_s,
    'imm8':     _imm_to_s,
    'imm11':    _imm_to_s,
    'rl8':      _rlist9_to_s,
    'rl9':      _rlist9_to_s,
    'cond':     _cond_to_s,
}


def ibonito(tipo: str, operandos: list) -> list:
    result = []
    for i, optipo in enumerate(SET[tipo][2]):
        result.append(OPTOS[optipo](operandos[i]))
    return result


# ── Disassembly string formatters ───────────────────────────────────────────

def _base_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ''
    for i, op in enumerate(op_s):
        cad += ' ' + op
        if i < len(op_s) - 1:
            cad += ','
    return SET[tipo][0] + (itcond if itcond is not None else 's') + cad


def _basef_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ''
    for i, op in enumerate(op_s):
        cad += ' ' + op
        if i < len(op_s) - 1:
            cad += ','
    return SET[tipo][0] + (itcond if itcond is not None else '') + cad


def _nomod_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ''
    for i, op in enumerate(op_s):
        cad += ' ' + op
        if i < len(op_s) - 1:
            cad += ','
    return SET[tipo][0] + cad


def _basenoit_to_s(tipo, operandos, itcond):
    if itcond is not None:
        return 'ERROR: no permitida en bloque IT'
    op_s = ibonito(tipo, operandos)
    cad = ''
    for i, op in enumerate(op_s):
        cad += ' ' + op
        if i < len(op_s) - 1:
            cad += ','
    return SET[tipo][0] + cad


def _lslit1_to_s(tipo, operandos, itcond):
    if operandos[2] == 0:
        op_s = ibonito(tipo, operandos)
        if itcond is not None:
            return 'ERROR: no permitida en bloque IT'
        return 'movs ' + op_s[0] + ', ' + op_s[1]
    return _base_to_s(tipo, operandos, itcond)


def _rsbt1_to_s(tipo, operandos, itcond):
    return _base_to_s(tipo, operandos, itcond) + ', #0'


def _unpred_to_s(tipo, operandos, itcond):
    return 'ERROR: unpredictable'


def _undef_to_s(tipo, operandos, itcond):
    return 'ERROR: undefined'


def _idxbase_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ' ' + op_s[0] + ', [' + op_s[1] + ', ' + op_s[2] + ']'
    return SET[tipo][0] + (itcond if itcond is not None else '') + cad


def _idx_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ' ' + op_s[0] + ', [' + op_s[1] + ']'
    return SET[tipo][0] + (itcond if itcond is not None else '') + cad


def _idxsp_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ' ' + op_s[0] + ', [sp, ' + op_s[1] + ']'
    return SET[tipo][0] + (itcond if itcond is not None else '') + cad


def _opsp_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    if len(op_s) == 2:
        cad = ' ' + op_s[0] + ', sp, ' + op_s[1]
    else:
        cad = ' sp, sp, ' + op_s[0]
    return SET[tipo][0] + (itcond if itcond is not None else '') + cad


def _oppc_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ' ' + op_s[0] + ', pc, ' + op_s[1]
    return SET[tipo][0] + (itcond if itcond is not None else '') + cad


def _idxpc_to_s(tipo, operandos, itcond):
    op_s = ibonito(tipo, operandos)
    cad = ' ' + op_s[0] + ', [pc, ' + op_s[1] + ']'
    return SET[tipo][0] + (itcond if itcond is not None else '') + cad


def _cps_to_s(tipo, operandos, itcond):
    if itcond is not None:
        return 'ERROR: no permitida en bloque IT'
    cad = 'i' + ('e' if operandos[0] == 0 else 'd') + ' '
    if operandos[1] & 2:
        cad += 'i'
    if operandos[1] & 1:
        cad += 'f'
    return SET[tipo][0] + cad


def _push_to_s(tipo, operandos, itcond):
    return _basef_to_s(tipo, operandos, itcond).replace('x', 'lr', 1)


def _pop_to_s(tipo, operandos, itcond):
    return _basef_to_s(tipo, operandos, itcond).replace('x', 'pc', 1)


def _stm_to_s(tipo, operandos, itcond):
    return _basef_to_s(tipo, operandos, itcond).replace(',', '!,', 1)


def _ldm_to_s(tipo, operandos, itcond):
    cad = _basef_to_s(tipo, operandos, itcond)
    if (operandos[1] & (1 << operandos[0])) == 0:
        cad = cad.replace(',', '!,', 1)
    return cad


def _bcond_to_s(tipo, operandos, itcond):
    if itcond is not None:
        return 'ERROR: no permitida en bloque IT'
    op_s = ibonito(tipo, operandos)
    return SET[tipo][0] + op_s[0] + ' ' + op_s[1]


def _it_to_s(tipo, operandos, itcond):
    global _itlist
    if itcond is not None:
        return 'ERROR: no permitida en bloque IT'
    op_s = ibonito(tipo, operandos)
    inst = 3
    mask = 1
    _itlist = [op_s[1]]
    cnum = operandos[1]
    while (operandos[0] & mask) == 0:
        inst -= 1
        mask <<= 1
    cuno = 1
    mask = 8
    cad = ''
    bit = operandos[1] & 1
    for _ in range(inst):
        if (operandos[0] & mask) != 0:
            cuno += 1
            cad += 't' if bit == 1 else 'e'
            _itlist.append(CONCODES[cnum] if bit == 1 else CONCODES[cnum - 1])
        else:
            cad += 'e' if bit == 1 else 't'
            _itlist.append(CONCODES[cnum + 1] if bit == 1 else CONCODES[cnum])
        mask //= 2
    if operandos[1] == 15 or (operandos[1] == 14 and cuno > 1):
        _itlist = None
        cad = 'ERROR: unpredictable'
    else:
        cad += ' ' + op_s[1]
        return SET[tipo][0] + cad
    return cad


FSET = {
    'lslit1':   _lslit1_to_s,
    'lsrit1':   _base_to_s,
    'asrit1':   _base_to_s,
    'movit1':   _base_to_s,
    'cmpit1':   _basef_to_s,
    'addit2':   _base_to_s,
    'subit2':   _base_to_s,
    'addrt1':   _base_to_s,
    'subrt1':   _base_to_s,
    'addit1':   _base_to_s,
    'subit1':   _base_to_s,
    'andrt1':   _base_to_s,
    'eorrt1':   _base_to_s,
    'lslrt1':   _base_to_s,
    'lsrrt1':   _base_to_s,
    'asrrt1':   _base_to_s,
    'adcrt1':   _base_to_s,
    'sbcrt1':   _base_to_s,
    'rorrt1':   _base_to_s,
    'tstrt1':   _basef_to_s,
    'rsbrt1':   _rsbt1_to_s,
    'cmprt1':   _basef_to_s,
    'cmnrt1':   _basef_to_s,
    'orrrt1':   _base_to_s,
    'mult1':    _base_to_s,
    'bicrt1':   _base_to_s,
    'mvnrt1':   _base_to_s,
    'addrt2':   _basef_to_s,
    'unpred':   _unpred_to_s,
    'cmprt2':   _basef_to_s,
    'movrt1':   _basef_to_s,
    'bxt1':     _basef_to_s,
    'blxt1':    _basef_to_s,
    'ldrlt1':   _idxpc_to_s,
    'strrt1':   _idxbase_to_s,
    'strhrt1':  _idxbase_to_s,
    'strbrt1':  _idxbase_to_s,
    'ldrsbrt1': _idxbase_to_s,
    'ldrrt1':   _idxbase_to_s,
    'ldrhrt1':  _idxbase_to_s,
    'ldrbrt1':  _idxbase_to_s,
    'ldrshrt1': _idxbase_to_s,
    'strit1':   _idxbase_to_s,
    'ldrit1':   _idxbase_to_s,
    'strbit1':  _idxbase_to_s,
    'ldrbit1':  _idxbase_to_s,
    'strhit1':  _idxbase_to_s,
    'ldrhit1':  _idxbase_to_s,
    'strit2':   _idxsp_to_s,
    'ldrit2':   _idxsp_to_s,
    'adrit1':   _oppc_to_s,
    'addspit1': _opsp_to_s,
    'addspit2': _opsp_to_s,
    'subspit1': _opsp_to_s,
    'cbzt1':    _basenoit_to_s,
    'sxtht1':   _basef_to_s,
    'sxtbt1':   _basef_to_s,
    'uxtht1':   _basef_to_s,
    'uxtbt1':   _basef_to_s,
    'pusht1':   _push_to_s,
    'cpst1':    _cps_to_s,
    'cbnzt1':   _basenoit_to_s,
    'revt1':    _basef_to_s,
    'rev16t1':  _basef_to_s,
    'revsht1':  _basef_to_s,
    'popt1':    _pop_to_s,
    'bkptt1':   _nomod_to_s,
    'stmt1':    _stm_to_s,
    'ldmt1':    _ldm_to_s,
    'udef':     _undef_to_s,
    'svct1':    _basef_to_s,
    'bt1':      _bcond_to_s,
    'bt2':      _basenoit_to_s,
    'nopt1':    _basef_to_s,
    'yieldt1':  _basef_to_s,
    'wfet1':    _basef_to_s,
    'wfit1':    _basef_to_s,
    'sevt1':    _basef_to_s,
    'itt1':     _it_to_s,
    'blt1':     _basenoit_to_s,
    'bt4':      _basenoit_to_s,
}


def instr_to_s(tipo: str, operandos: list, addr: int, cond=None) -> str:
    global _address, _itlist
    _address = addr
    if _itlist is not None:
        cond = _itlist.pop(0) if _itlist else None
        if not _itlist:
            _itlist = None
    return FSET[tipo](tipo, operandos, cond)


# ── Processor reset ─────────────────────────────────────────────────────────

def reset() -> dict:
    """Return initial processor state: 16 zero registers, all flags 0."""
    return {
        'usr_regs': [0] * 16,
        'flags': {'c': 0, 'z': 0, 'n': 0, 'v': 0},
    }


# ── Operand preparation functions (PSET) ────────────────────────────────────

def _basi1r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'f2': operandos[1], 'c': 0, 'd': operandos[0]}


def _basi2r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[1]],
            'f2': operandos[2], 'c': 0, 'd': operandos[0]}


def _bas3r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[1]],
            'f2': estado['usr_regs'][operandos[2]], 'c': 0, 'd': operandos[0]}


def _bas2r16_p(operandos, estado):
    return {'fg': False, 'f1': estado['usr_regs'][operandos[0]],
            'f2': estado['usr_regs'][operandos[1]], 'c': 0, 'd': operandos[0]}


def _bas2r16c_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'f2': estado['usr_regs'][operandos[1]],
            'c': estado['flags']['c'], 'd': operandos[0]}


def _addrsp_p(operandos, estado):
    return {'fg': False, 'f1': estado['usr_regs'][SP],
            'f2': operandos[1] * 4, 'c': 0, 'd': operandos[0]}


def _addrpc_p(operandos, estado):
    return {'fg': False, 'f1': (estado['usr_regs'][PC] & 0xFFFFFFFC) + 4,
            'f2': operandos[1] * 4, 'c': 0, 'd': operandos[0]}


def _addisp_p(operandos, estado):
    return {'fg': False, 'f1': estado['usr_regs'][SP],
            'f2': operandos[0] * 4, 'c': 0, 'd': 13}


def _subi1r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'f2': (~operandos[1]) & 0xFFFFFFFF, 'c': 1, 'd': operandos[0]}


def _subi2r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[1]],
            'f2': (~operandos[2]) & 0xFFFFFFFF, 'c': 1, 'd': operandos[0]}


def _sub3r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[1]],
            'f2': (~estado['usr_regs'][operandos[2]]) & 0xFFFFFFFF,
            'c': 1, 'd': operandos[0]}


def _subisp_p(operandos, estado):
    return {'fg': False, 'f1': estado['usr_regs'][SP],
            'f2': (~(operandos[0] * 4)) & 0xFFFFFFFF, 'c': 1, 'd': 13}


def _sbc2r16c_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'f2': (~estado['usr_regs'][operandos[1]]) & 0xFFFFFFFF,
            'c': estado['flags']['c'], 'd': operandos[0]}


def _rsb2r16_p(operandos, estado):
    return {'fg': True, 'f1': (~estado['usr_regs'][operandos[1]]) & 0xFFFFFFFF,
            'f2': 0, 'c': 1, 'd': operandos[0]}


def _cmpi1r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'f2': (~operandos[1]) & 0xFFFFFFFF, 'c': 1}


def _cmp2r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'f2': (~estado['usr_regs'][operandos[1]]) & 0xFFFFFFFF, 'c': 1}


def _cmn2r16_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'f2': estado['usr_regs'][operandos[1]], 'c': 0}


def _mvn2r16_p(operandos, estado):
    return {'fg': True, 'f1': (~estado['usr_regs'][operandos[1]]) & 0xFFFFFFFF,
            'd': operandos[0]}


def _mov2r16_p(operandos, estado):
    return {'fg': False, 'f1': estado['usr_regs'][operandos[1]], 'd': operandos[0]}


def _movi16_p(operandos, estado):
    return {'fg': True, 'f1': operandos[1], 'd': operandos[0]}


def _ldripc_p(operandos, estado):
    addr = operandos[1] * 4 + (estado['usr_regs'][PC] & 0xFFFFFFFC) + 4
    f1 = estado['memory'].access('rw', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _str3rw_p(operandos, estado):
    return {'f': estado['usr_regs'][operandos[0]],
            'b': estado['usr_regs'][operandos[1]],
            'o': estado['usr_regs'][operandos[2]], 's': 'ww'}


def _str3rh_p(operandos, estado):
    return {'f': estado['usr_regs'][operandos[0]],
            'b': estado['usr_regs'][operandos[1]],
            'o': estado['usr_regs'][operandos[2]], 's': 'wh'}


def _str3rb_p(operandos, estado):
    return {'f': estado['usr_regs'][operandos[0]],
            'b': estado['usr_regs'][operandos[1]],
            'o': estado['usr_regs'][operandos[2]], 's': 'wb'}


def _ldrsbr_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + estado['usr_regs'][operandos[2]]
    f1 = estado['memory'].access('rb', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    if not (f1 & 0x80) == 0:
        f1 = 0xFFFFFF00 | f1
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _ldrwr_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + estado['usr_regs'][operandos[2]]
    f1 = estado['memory'].access('rw', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _ldrhr_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + estado['usr_regs'][operandos[2]]
    f1 = estado['memory'].access('rh', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _ldrbr_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + estado['usr_regs'][operandos[2]]
    f1 = estado['memory'].access('rb', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _ldrshr_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + estado['usr_regs'][operandos[2]]
    f1 = estado['memory'].access('rh', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    if not (f1 & 0x8000) == 0:
        f1 = 0xFFFF0000 | f1
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _str2riw_p(operandos, estado):
    return {'f': estado['usr_regs'][operandos[0]],
            'b': estado['usr_regs'][operandos[1]],
            'o': operandos[2] * 4, 's': 'ww'}


def _str2rih_p(operandos, estado):
    return {'f': estado['usr_regs'][operandos[0]],
            'b': estado['usr_regs'][operandos[1]],
            'o': operandos[2] * 2, 's': 'wh'}


def _str2rib_p(operandos, estado):
    return {'f': estado['usr_regs'][operandos[0]],
            'b': estado['usr_regs'][operandos[1]],
            'o': operandos[2], 's': 'wb'}


def _ldrwi_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + operandos[2] * 4
    f1 = estado['memory'].access('rw', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _ldrhi_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + operandos[2] * 2
    f1 = estado['memory'].access('rh', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _ldrbi_p(operandos, estado):
    addr = estado['usr_regs'][operandos[1]] + operandos[2]
    f1 = estado['memory'].access('rb', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _strisp_p(operandos, estado):
    return {'f': estado['usr_regs'][operandos[0]],
            'b': estado['usr_regs'][SP],
            'o': operandos[1] * 4, 's': 'ww'}


def _ldrisp_p(operandos, estado):
    addr = estado['usr_regs'][SP] + operandos[1] * 4
    f1 = estado['memory'].access('rw', addr)
    if isinstance(f1, str):
        return {'error': [f1, addr]}
    return {'fg': False, 'f1': f1, 'd': operandos[0]}


def _lsli_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[1]],
            'sa': operandos[2], 'd': operandos[0]}


def _dsri_p(operandos, estado):
    sa = 32 if operandos[2] == 0 else operandos[2]
    return {'fg': True, 'f1': estado['usr_regs'][operandos[1]],
            'sa': sa, 'd': operandos[0]}


def _shiftr_p(operandos, estado):
    return {'fg': True, 'f1': estado['usr_regs'][operandos[0]],
            'sa': estado['usr_regs'][operandos[1]] & 0xFF, 'd': operandos[0]}


def _bx_p(operandos, estado):
    return {'fg': False, 'f1': estado['usr_regs'][operandos[0]], 'd': PC}


def _blx_p(operandos, estado):
    return {'f1': estado['usr_regs'][operandos[0]],
            'f2': (estado['usr_regs'][PC] & 0xFFFFFFFE) + 4,
            'd1': PC, 'd2': LR}


def _cbz_p(operandos, estado):
    return {'f1': (estado['usr_regs'][PC] & 0xFFFFFFFE) + 4,
            'f2': operandos[1] * 2,
            'cn': estado['usr_regs'][operandos[0]] == 0}


def _cbnz_p(operandos, estado):
    return {'f1': (estado['usr_regs'][PC] & 0xFFFFFFFC) + 4,
            'f2': operandos[1] * 2,
            'cn': estado['usr_regs'][operandos[0]] != 0}


def _ldm_p(operandos, estado):
    if len(operandos) == 2:
        base = operandos[0]
        lista = operandos[1] & 0xFF
    else:
        base = SP
        lista = operandos[0] & 0x1FF
    addr = estado['usr_regs'][base]
    dest = []
    fnt = []
    esta = False
    data = None
    l = lista
    for ind in range(8):
        if l & 1:
            if base == ind:
                esta = True
            acok = estado['memory'].access('rw', addr)
            if isinstance(acok, str):
                data = {'error': [acok, addr]}
                break
            fnt.append(acok)
            dest.append(ind)
            addr += 4
        l >>= 1
    if data is None and l & 1:
        acok = estado['memory'].access('rw', addr)
        if isinstance(acok, str):
            data = {'error': [acok, addr]}
        else:
            dest.append(PC)
            fnt.append(acok)
            addr += 4
    if not esta:
        dest.append(base)
        fnt.append(addr)
    if data is None:
        data = {'f1': fnt, 'd': dest}
    else:
        data['f1'] = fnt
        data['d'] = dest
    return data


def _stm_p(operandos, estado):
    base = operandos[0]
    lista = operandos[1] & 0xFF
    addr = estado['usr_regs'][base]
    dest = []
    fnt = []
    l = lista
    for ind in range(8):
        if l & 1:
            dest.append(estado['usr_regs'][ind])
            fnt.append(addr)
            addr += 4
        l >>= 1
    return {'f1': fnt, 'd1': dest, 'f2': addr, 'd2': base}


def _push_p(operandos, estado):
    lista = operandos[0] & 0x1FF
    addr = estado['usr_regs'][SP] - 4
    dest = []
    fnt = []
    l = lista
    for ind in range(8):
        if l & 1:
            dest.append(estado['usr_regs'][ind])
            fnt.append(addr)
            addr -= 4
        l >>= 1
    if l & 1:
        dest.append(estado['usr_regs'][LR])
        fnt.append(addr)
        addr -= 4
    dest.reverse()
    return {'f1': fnt, 'd1': dest, 'f2': addr + 4, 'd2': SP}


def _babs_p(operandos, estado):
    f1 = (estado['usr_regs'][PC] & 0xFFFFFFFE) + 4
    f2 = operandos[0] * 2
    f2 = f2 | 0xFFFFF000 if f2 & 0x800 else f2 & 0xFFF
    return {'f1': f1, 'f2': f2, 'cn': True}


def _bcond_p(operandos, estado):
    f1 = (estado['usr_regs'][PC] & 0xFFFFFFFE) + 4
    f2 = operandos[1] * 2
    f2 = f2 | 0xFFFFFE00 if f2 & 0x100 else f2 & 0x1FF
    cn = eval_cond(operandos[0], estado['flags'])
    return {'f1': f1, 'f2': f2, 'cn': cn}


def _nop_p(operandos, estado):
    return {}


def _blt1_p(operandos, estado):
    numero = operandos[0]
    imm11 = numero & 0x7FF
    imm10 = (numero & 0x03FF0000) >> 5
    s  = 0 if (numero & 0x04000000) == 0 else 1
    j1 = 0 if (numero & 0x02000)    == 0 else 1
    j2 = 0 if (numero & 0x0800)     == 0 else 1
    i1 = 1 if s == j1 else 0
    i2 = 1 if s == j2 else 0
    imm3 = (s * 4 + i1 * 2 + i2) << 21
    imm = ((imm3 & 0x0E00000) | (imm10 & 0x1FF800) | imm11) * 2
    imm = (0xFE000000 | imm) if s == 1 else (0x1FFFFFF & imm)
    f2 = (estado['usr_regs'][PC] & 0xFFFFFFFE) + 4
    f1 = (f2 + imm) & 0xFFFFFFFF
    return {'f1': f1, 'f2': f2, 'd1': PC, 'd2': LR}


def _bt4_p(operandos, estado):
    numero = operandos[0]
    imm11 = numero & 0x7FF
    imm10 = (numero & 0x03FF0000) >> 5
    s  = 0 if (numero & 0x04000000) == 0 else 1
    j1 = 0 if (numero & 0x02000)    == 0 else 1
    j2 = 0 if (numero & 0x0800)     == 0 else 1
    i1 = 1 if s == j1 else 0
    i2 = 1 if s == j2 else 0
    imm3 = (s * 4 + i1 * 2 + i2) << 21
    imm = ((imm3 & 0x0E00000) | (imm10 & 0x1FF800) | imm11) * 2
    imm = (0xFE000000 | imm) if s == 1 else (0x1FFFFFF & imm)
    f1 = (estado['usr_regs'][PC] & 0xFFFFFFFE) + 4
    return {'f1': f1, 'f2': imm & 0xFFFFFFFF, 'cn': True}


PSET: dict = {
    'lslit1':   _lsli_p,
    'lsrit1':   _dsri_p,
    'asrit1':   _dsri_p,
    'movit1':   _movi16_p,
    'cmpit1':   _cmpi1r16_p,
    'addit2':   _basi1r16_p,
    'subit2':   _subi1r16_p,
    'addrt1':   _bas3r16_p,
    'subrt1':   _sub3r16_p,
    'addit1':   _basi2r16_p,
    'subit1':   _subi2r16_p,
    'andrt1':   _bas2r16c_p,
    'eorrt1':   _bas2r16c_p,
    'lslrt1':   _shiftr_p,
    'lsrrt1':   _shiftr_p,
    'asrrt1':   _shiftr_p,
    'adcrt1':   _bas2r16c_p,
    'sbcrt1':   _sbc2r16c_p,
    'rorrt1':   _shiftr_p,
    'tstrt1':   _cmn2r16_p,
    'rsbrt1':   _rsb2r16_p,
    'cmprt1':   _cmp2r16_p,
    'cmnrt1':   _cmn2r16_p,
    'orrrt1':   _bas2r16c_p,
    'mult1':    _bas2r16c_p,
    'bicrt1':   _sbc2r16c_p,
    'mvnrt1':   _mvn2r16_p,
    'addrt2':   _bas2r16_p,
    'unpred':   _nop_p,
    'cmprt2':   _cmp2r16_p,
    'movrt1':   _mov2r16_p,
    'bxt1':     _bx_p,
    'blxt1':    _blx_p,
    'ldrlt1':   _ldripc_p,
    'strrt1':   _str3rw_p,
    'strhrt1':  _str3rh_p,
    'strbrt1':  _str3rb_p,
    'ldrsbrt1': _ldrsbr_p,
    'ldrrt1':   _ldrwr_p,
    'ldrhrt1':  _ldrhr_p,
    'ldrbrt1':  _ldrbr_p,
    'ldrshrt1': _ldrshr_p,
    'strit1':   _str2riw_p,
    'ldrit1':   _ldrwi_p,
    'strbit1':  _str2rib_p,
    'ldrbit1':  _ldrbi_p,
    'strhit1':  _str2rih_p,
    'ldrhit1':  _ldrhi_p,
    'strit2':   _strisp_p,
    'ldrit2':   _ldrisp_p,
    'adrit1':   _addrpc_p,
    'addspit1': _addrsp_p,
    'addspit2': _addisp_p,
    'subspit1': _subisp_p,
    'cbzt1':    _cbz_p,
    'sxtht1':   _mov2r16_p,
    'sxtbt1':   _mov2r16_p,
    'uxtht1':   _mov2r16_p,
    'uxtbt1':   _mov2r16_p,
    'pusht1':   _push_p,
    'cpst1':    _nop_p,
    'cbnzt1':   _cbnz_p,
    'revt1':    _mov2r16_p,
    'rev16t1':  _mov2r16_p,
    'revsht1':  _mov2r16_p,
    'popt1':    _ldm_p,
    'bkptt1':   _nop_p,
    'stmt1':    _stm_p,
    'ldmt1':    _ldm_p,
    'udef':     _nop_p,
    'svct1':    _nop_p,
    'bt1':      _bcond_p,
    'bt2':      _babs_p,
    'nopt1':    _nop_p,
    'yieldt1':  _nop_p,
    'wfet1':    _nop_p,
    'wfit1':    _nop_p,
    'sevt1':    _nop_p,
    'itt1':     _it_to_s,   # same as display for IT
    'blt1':     _blt1_p,
    'bt4':      _bt4_p,
}

# ── Execution functions (ESET) ───────────────────────────────────────────────

def _add_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    op1 = op['f1']
    op2 = op['f2']
    eop1 = op1 + ((op1 & 0x80000000) << 1)
    eop2 = op2 + ((op2 & 0x80000000) << 1)
    ures = op1 + op2 + op['c']
    eres = eop1 + eop2 + op['c']
    res = ures & 0xFFFFFFFF
    if op.get('fg'):
        z = 1 if res == 0 else 0
        n = 0 if (res & 0x80000000) == 0 else 1
        c = 0 if res == ures else 1
        dbits = (eres & 0x180000000) >> 31
        v = 1 if dbits in (1, 2) else 0
        data['flags'] = {'c': c, 'v': v, 'z': z, 'n': n}
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _and_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    res = op['f1'] & op['f2']
    if op.get('fg'):
        data['flags'] = {'z': 1 if res == 0 else 0,
                         'n': 0 if (res & 0x80000000) == 0 else 1}
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _eor_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    res = op['f1'] ^ op['f2']
    if op.get('fg'):
        data['flags'] = {'z': 1 if res == 0 else 0,
                         'n': 0 if (res & 0x80000000) == 0 else 1}
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _orr_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    res = op['f1'] | op['f2']
    if op.get('fg'):
        data['flags'] = {'z': 1 if res == 0 else 0,
                         'n': 0 if (res & 0x80000000) == 0 else 1}
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _mov_e(op):
    data: dict = {}
    if op.get('error') is None:
        if op.get('d') is not None:
            data['usr_regs'] = [op['d']]
        res = op['f1']
        if op.get('fg'):
            data['flags'] = {'z': 1 if res == 0 else 0,
                             'n': 0 if (res & 0x80000000) == 0 else 1}
        if op.get('d') is not None:
            data['usr_regs'].append(res)
    else:
        data['error'] = op['error']
    return data


def _mul_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    res = (op['f1'] * op['f2']) & 0xFFFFFFFF
    if op.get('fg'):
        data['flags'] = {'z': 1 if res == 0 else 0,
                         'n': 0 if (res & 0x80000000) == 0 else 1}
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _str_e(op):
    mask = {'ww': 0xFFFFFFFF, 'wh': 0xFFFF, 'wb': 0xFF}
    return {'memory': [op['s'], [[op['b'] + op['o'], op['f'] & mask[op['s']]]]]}


def _lsl_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    sa = op['sa']
    f1 = op['f1']
    if sa == 0:
        res = f1
        c = None
    else:
        c = 0 if ((f1 << (sa - 1)) & 0x80000000) == 0 else 1
        res = (f1 << sa) & 0xFFFFFFFF
    if op.get('fg'):
        data['flags'] = {'z': 1 if res == 0 else 0,
                         'n': 0 if (res & 0x80000000) == 0 else 1}
        if sa != 0:
            data['flags']['c'] = c
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _asr_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    sa = op['sa']
    f1 = op['f1']
    if sa == 0:
        res = f1
        c = None
    else:
        c = (f1 >> (sa - 1)) & 1
        msc = (0xFFFFFFFF << (32 - sa)) & 0xFFFFFFFF
        res = f1 >> sa
        if (f1 & 0x80000000):
            res = res | msc
        res &= 0xFFFFFFFF
    if op.get('fg'):
        data['flags'] = {'z': 1 if res == 0 else 0,
                         'n': 0 if (res & 0x80000000) == 0 else 1}
        if sa != 0:
            data['flags']['c'] = c
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _lsr_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    sa = op['sa']
    f1 = op['f1']
    if sa == 0:
        res = f1
        c = None
    else:
        c = (f1 >> (sa - 1)) & 1
        res = (f1 >> sa) & (0xFFFFFFFF >> sa)
    if op.get('fg'):
        data['flags'] = {'z': 1 if res == 0 else 0,
                         'n': 0 if (res & 0x80000000) == 0 else 1}
        if sa != 0:
            data['flags']['c'] = c
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _ror_e(op):
    data: dict = {}
    if op.get('d') is not None:
        data['usr_regs'] = [op['d']]
    sa = op['sa']
    f1 = op['f1']
    if sa == 0:
        res = f1
    else:
        desp = sa & 0x1F
        if desp == 0:
            res = f1
        else:
            res = ((f1 >> desp) | (f1 << (32 - desp))) & 0xFFFFFFFF
    if op.get('fg'):
        n = 0 if (res & 0x80000000) == 0 else 1
        data['flags'] = {'z': 1 if res == 0 else 0, 'n': n}
        if sa != 0:
            data['flags']['c'] = n  # C = bit 31 of result
    if op.get('d') is not None:
        data['usr_regs'].append(res)
    return data


def _blx_e(op):
    return {'usr_regs': [op['d1'], op['f1'], op['d2'], op['f2']]}


def _cbxz_e(op):
    if op.get('cn'):
        return {'usr_regs': [PC, op['f1'] + op['f2']]}
    return {}


def _sxth_e(op):
    f1 = op['f1']
    valor = (f1 | 0xFFFF0000) if f1 & 0x8000 else (f1 & 0xFFFF)
    return {'usr_regs': [op['d'], valor]}


def _sxtb_e(op):
    f1 = op['f1']
    valor = (f1 | 0xFFFFFF00) if f1 & 0x80 else (f1 & 0xFF)
    return {'usr_regs': [op['d'], valor]}


def _uxth_e(op):
    return {'usr_regs': [op['d'], op['f1'] & 0xFFFF]}


def _uxtb_e(op):
    return {'usr_regs': [op['d'], op['f1'] & 0xFF]}


def _rev_e(op):
    v = op['f1']
    val = (((v << 24) & 0xFF000000) | ((v << 8) & 0xFF0000) |
           ((v >> 8) & 0xFF00) | ((v >> 24) & 0xFF))
    return {'usr_regs': [op['d'], val]}


def _rev16_e(op):
    v = op['f1']
    val = ((v << 8) & 0xFF00FF00) | ((v >> 8) & 0x00FF00FF)
    return {'usr_regs': [op['d'], val]}


def _revsh_e(op):
    v = op['f1']
    val = ((v << 8) & 0xFF00) | ((v >> 8) & 0xFF)
    val = (val | 0xFFFF0000) if val & 0x8000 else (val & 0xFFFF)
    return {'usr_regs': [op['d'], val]}


def _ldm_e(op):
    data: dict = {}
    if op.get('d') is not None:
        res = []
        for i, item in enumerate(op['d']):
            res.append(item)
            res.append(op['f1'][i])
        data['usr_regs'] = res
    if op.get('error') is not None:
        data['error'] = op['error']
    return data


def _stm_e(op):
    res = []
    for i, item in enumerate(op['d1']):
        res.append([op['f1'][i], item])
    return {'usr_regs': [op['d2'], op['f2']], 'memory': ['ww', res]}


def _nop_e(op):
    return {}


ESET: dict = {
    'add':   _add_e,
    'and':   _and_e,
    'eor':   _eor_e,
    'orr':   _orr_e,
    'mov':   _mov_e,
    'mul':   _mul_e,
    'ldr':   _mov_e,
    'str':   _str_e,
    'strh':  _str_e,
    'strb':  _str_e,
    'adr':   _add_e,
    'lsl':   _lsl_e,
    'lsr':   _lsr_e,
    'asr':   _asr_e,
    'ror':   _ror_e,
    'bx':    _mov_e,
    'blx':   _blx_e,
    'cbz':   _cbxz_e,
    'cbnz':  _cbxz_e,
    'sxth':  _sxth_e,
    'sxtb':  _sxtb_e,
    'uxth':  _uxth_e,
    'uxtb':  _uxtb_e,
    'rev':   _rev_e,
    'rev16': _rev16_e,
    'revsh': _revsh_e,
    'ldm':   _ldm_e,
    'pop':   _ldm_e,
    'stm':   _stm_e,
    'push':  _stm_e,
    'unp':   _nop_e,
    'cps':   _nop_e,
    'bkpt':  _nop_e,
    'und':   _nop_e,
    'svc':   _nop_e,
    'yield': _nop_e,
    'wfe':   _nop_e,
    'wfi':   _nop_e,
    'sev':   _nop_e,
    'b':     _cbxz_e,
    'nop':   _nop_e,
    'it':    _nop_e,
}


def prep_data(tipo: str, operandos: list, estado: dict) -> dict:
    fn = PSET.get(tipo)
    if fn is None:
        return {}
    result = fn(operandos, estado)
    return result if result is not None else {}


def execute(tipo: str, datos: dict) -> dict:
    op_id = SET[tipo][1]
    fn = ESET.get(op_id, _nop_e)
    return fn(datos)
