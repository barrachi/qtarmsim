# -*- coding: utf-8 -*-
# ELF file parser for ARM simulator.
# Translated from read_ELF.rb and the read_ELF() function in server.rb.

import struct

import memory_defs  # pyright: ignore[reportMissingImports]
from memory_block import MemoryBlock  # pyright: ignore[reportMissingImports]

ACESSES = memory_defs.RAM_LE_NA

ELFCLASS   = ['Invalid object', '32 bit object', '64 bit object']
ELFDATA    = ['Invalid data', 'LSB data', 'MSB data']
ELFVERSION = ['Invalid version', 'Current version']
ELFTYPE    = ['Invalid type', 'Object file', 'Executable file', 'Shared object file']
ELFSECTYPES = [
    'Inactiva', 'Definida por el programa', 'Tabla de simbolos',
    'Tabla de strings', 'Tabla de reubicacion con datos',
    'Tabla hash de simbolos', 'Informacion para el enlazado dinamico',
    'Notas', 'No bits', 'Tabla de reubicacion', 'Reservado',
    'Tabla de simbolos dinamicos',
]
ELFSYMBIND = ['Local', 'Global', 'Weak']
ELFSYMTYPE = ['No type', 'Data object', 'Function or code', 'Section', 'File']

STT_FUNC   = 2
SHN_COMMON = 65522
SHN_NAME   = 65521

ORIG_CODE   = 0x00180000
ORIG_DATA   = 0x20070000
END_DATA    = 0x20070800
ORIG_EXTERN = 0x00004000
SIZE_EXTERN = 16

# NOP instruction bytes (little-endian 0xBF30 = NOP T1)
BLOCK0 = [0x30, 0xBF]


class ELFFile:
    """Parses an ARM ELF32 relocatable object file."""

    def __init__(self, path: str):
        self._path = path
        self._data: bytes = b''
        self._pos: int = 0
        self.sections: list = []
        self.symbols: list = []
        self.relocations: list = []
        self.section_names_idx: int = 0
        self.string_table_idx: int = 0
        self.sym_table_idx: int = 0
        self.rel_idx: list[int] = []
        self.wks: dict = {'.text': 0, '.rodata': 0, '.data': 0, '.bss': 0}
        self.wks_orig: dict = {
            '.text':   ORIG_CODE,
            '.rodata': 0,
            '.data':   ORIG_DATA,
            '.bss':    0,
        }
        self.extern_symbols: dict | None = None

    def _read_bytes(self, n: int) -> bytes:
        chunk = self._data[self._pos:self._pos + n]
        self._pos += n
        return chunk

    def _seek(self, pos: int) -> None:
        self._pos = pos

    def get_byte(self) -> int:
        b = self._data[self._pos]
        self._pos += 1
        return b

    def get_half(self) -> int:
        lo = self.get_byte()
        hi = self.get_byte()
        return lo + hi * 256

    def get_word(self) -> int:
        b0 = self.get_byte()
        b1 = self.get_byte()
        b2 = self.get_byte()
        b3 = self.get_byte()
        return b0 + 256 * (b1 + 256 * (b2 + 256 * b3))

    def get_array(self, n: int) -> list[int]:
        return [self.get_byte() for _ in range(n)]

    def get_section_hdr(self) -> dict:
        fields = ['name', 'type', 'flags', 'addr', 'offset', 'size',
                  'link', 'info', 'addralign', 'entsize']
        return {f: self.get_word() for f in fields}

    def get_symbol_entry(self) -> dict:
        name  = self.get_word()
        value = self.get_word()
        size  = self.get_word()
        info  = self.get_byte()
        other = self.get_byte()
        shndx = self.get_half()
        return {'name': name, 'value': value, 'size': size,
                'info': info, 'other': other, 'shndx': shndx}

    def get_relocation_entry(self) -> dict:
        return {'offset': self.get_word(), 'info': self.get_word()}

    def read_section_bytes(self, idx: int) -> list[int]:
        sec = self.sections[idx]
        self._seek(sec['header']['offset'])
        return self.get_array(sec['header']['size'])

    def fill_section(self, idx: int) -> None:
        self.sections[idx]['data'] = self.read_section_bytes(idx)

    def _get_string(self, sec_idx: int, offset: int) -> str:
        data = self.sections[sec_idx]['data']
        result = ''
        while data[offset] != 0:
            result += chr(data[offset])
            offset += 1
        return result

    def get_section_name_string(self, offset: int) -> str:
        return self._get_string(self.section_names_idx, offset)

    def get_string_table_string(self, offset: int) -> str:
        return self._get_string(self.string_table_idx, offset)

    def relocate(self):
        """Apply relocations; return [code_block, data_block, symbol_table, bind_table]."""
        warnings: list[str] = []
        symbol_table: dict = {}
        bind_table: dict = {}

        code = (list(self.sections[self.wks['.text']].get('data') or []) or list(BLOCK0))
        data = list(self.sections[self.wks['.data']].get('data') or [0, 0, 0, 0])

        bssdir    = self.wks_orig['.bss']
        externdir = ORIG_EXTERN

        for symbol in self.symbols:
            symsection = symbol['data']['shndx']
            bind = (symbol['data']['info'] >> 4) & 0x0F
            if bind == 1 and symsection == 0:
                if self.extern_symbols is None or self.extern_symbols.get(symbol['name']) is None:
                    warnings.append("Símbolo «%s» no definido." % symbol['name'])
            if symsection == SHN_NAME:
                continue
            symname = ("SEC%d:S%d" % (symsection, symbol['idx'])
                       if len(symbol['name']) == 0 else symbol['name'])
            if symsection == SHN_COMMON:
                align = symbol['data']['value']
                if align and bssdir % align != 0:
                    bssdir += align - (bssdir % align)
                symaddress = bssdir
                bssdir += symbol['data']['size']
            elif symsection == 0:
                if self.extern_symbols is not None:
                    firmaddress = self.extern_symbols.get(symname)
                else:
                    firmaddress = None
                if firmaddress is None:
                    symaddress = externdir
                    externdir += SIZE_EXTERN
                else:
                    symaddress = firmaddress
            else:
                sec_name = self.sections[symsection].get('name')
                symaddress = self.wks_orig.get(sec_name)
                if symaddress is not None:
                    symaddress += symbol['data']['value']

            if symaddress is not None:
                if symbol['data']['info'] & 0x0F == STT_FUNC:
                    symaddress = symaddress & 0xFFFFFFFE
                symbol_table[symname] = symaddress
                bind_table[symname] = bind

        for idx, rel in enumerate(self.relocations):
            rel_sec_idx = self.rel_idx[idx]
            sec_info = self.sections[rel_sec_idx]['header']['info']
            dest = code if sec_info == self.wks['.text'] else data
            basedir = (self.wks_orig['.text'] if sec_info == self.wks['.text']
                       else self.wks_orig['.data'])
            orig = self.sections[sec_info].get('data', [])

            for entry in rel:
                sym_idx = entry['data']['info'] >> 8
                symbol = self.symbols[sym_idx]
                symsection = symbol['data']['shndx']
                symname = ("SEC%d:S%d" % (symsection, symbol['idx'])
                           if len(symbol['name']) == 0 else symbol['name'])
                symaddress = symbol_table.get(symname, 0)

                offset   = entry['data']['offset']
                poffset  = basedir + offset
                rel_type = entry['data']['info'] & 0xFF
                addend   = ACESSES['rw'](orig, offset)

                if rel_type == 2:
                    result = addend + symaddress
                elif rel_type == 10:
                    immediate = ((addend & 0x7FF) << 12) + ((addend & 0x7FF0000) >> 15)
                    if not (immediate & 0x400000) == 0:
                        immediate = immediate | 0xFF800000
                    result = ((immediate + (symaddress - poffset)) & 0xFFFFFFFF) >> 1
                    result = ((addend & 0xF800F800) |
                              ((result & 0x7FF) << 16) |
                              ((result & 0x3FF800) >> 11))
                elif rel_type == 102:
                    result = addend + ((symaddress - poffset) >> 1)
                elif rel_type == 103:
                    result = addend + ((symaddress - poffset) >> 1)
                else:
                    result = addend

                ACESSES['ww'](dest, offset, result)

        # Append .rodata to code
        rodata = self.sections[self.wks['.rodata']].get('data')
        if rodata:
            code += rodata

        # Pad data up to end of BSS
        dataend = bssdir if bssdir > END_DATA else END_DATA
        data += [0] * (dataend - self.wks_orig['.bss'] + 1)

        bcode = MemoryBlock(self.wks_orig['.text'], 0, 'rom_le', 0, 'ROM').fill_from_array(code)
        bdata = MemoryBlock(self.wks_orig['.data'], 0, 'ram_le', 0, 'RAM').fill_from_array(data)

        # Store warnings globally (accessible via module-level list)
        import sys
        _mod = sys.modules[__name__]
        setattr(_mod, '_last_warnings', warnings)

        return [bcode, bdata, symbol_table, bind_table]


_last_warnings: list[str] = []


def read_elf(filename: str, firmware: bool = False,
             firm_table: dict | None = None):
    """Parse an ELF32 ARM object file and return [code_block, data_block, symbols, binds]."""
    import os
    with open(filename, 'rb') as f:
        raw = f.read()

    elf = ELFFile(filename)
    elf._data = raw
    elf.extern_symbols = firm_table

    if firmware:
        elf.wks_orig['.text'] = 0x00190000

    # Read ELF header
    e_ident     = elf.get_array(16)
    _            = e_ident  # ignore magic check for now
    e_type      = elf.get_half()
    e_machine   = elf.get_half()
    e_version   = elf.get_word()
    e_entry     = elf.get_word()
    e_phoff     = elf.get_word()
    e_shoff     = elf.get_word()
    e_flags     = elf.get_word()
    e_ehsize    = elf.get_half()
    e_phentsize = elf.get_half()
    e_phnum     = elf.get_half()
    e_shentsize = elf.get_half()
    e_shnum     = elf.get_half()
    e_shstrndx  = elf.get_half()

    # Read section headers
    elf._seek(e_shoff)
    elf.sections = []
    st = 0
    stable = 0

    for idx in range(e_shnum):
        sec = {'idx': idx, 'header': elf.get_section_hdr(), 'data': None, 'name': ''}
        elf.sections.append(sec)
        htype = sec['header']['type']
        if htype == 3 and idx != e_shstrndx:
            st = idx
        if htype == 2:
            stable = idx
        if htype == 9:
            elf.rel_idx.append(idx)

    elf.section_names_idx = e_shstrndx
    elf.string_table_idx  = st
    elf.sym_table_idx     = stable

    elf.fill_section(e_shstrndx)
    elf.fill_section(st)
    for rel in elf.rel_idx:
        elf.fill_section(rel)

    # Name sections and collect well-known section indices
    for sec in elf.sections:
        sec['name'] = elf.get_section_name_string(sec['header']['name'])
        if sec['name'] in elf.wks:
            elf.wks[sec['name']] = sec['idx']

    # Calculate .rodata and .bss origins
    text_size = elf.sections[elf.wks['.text']]['header']['size']
    rodata_orig = elf.wks_orig['.text'] + text_size
    if rodata_orig % 4:
        rodata_orig += 4 - (rodata_orig % 4)
    elf.wks_orig['.rodata'] = rodata_orig
    elf.wks_orig['.bss'] = (elf.wks_orig['.data'] +
                             elf.sections[elf.wks['.data']]['header']['size'])

    # Read symbol table
    elf._seek(elf.sections[stable]['header']['offset'])
    num_syms = elf.sections[stable]['header']['size'] // elf.sections[stable]['header']['entsize']
    elf.symbols = []
    for idx in range(num_syms):
        sym = {
            'idx': idx,
            'data': elf.get_symbol_entry(),
            'name': '',
        }
        sym['name'] = elf.get_string_table_string(sym['data']['name'])
        elf.symbols.append(sym)

    # Read relocation tables
    for rel_sec_idx in elf.rel_idx:
        sec = elf.sections[rel_sec_idx]
        elf._seek(sec['header']['offset'])
        num_rel = sec['header']['size'] // sec['header']['entsize']
        rels = []
        for idx in range(num_rel):
            entry = {'idx': idx, 'data': elf.get_relocation_entry()}
            rels.append(entry)
        elf.relocations.append(rels)

    # Fill data sections
    if elf.sections[elf.wks['.text']]['header']['size'] > 0:
        elf.fill_section(elf.wks['.text'])
    if elf.sections[elf.wks['.data']]['header']['size'] > 0:
        elf.fill_section(elf.wks['.data'])
    if elf.sections[elf.wks['.rodata']]['header']['size'] > 0:
        elf.fill_section(elf.wks['.rodata'])

    return elf.relocate()
