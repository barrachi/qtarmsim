# -*- coding: utf-8 -*-

import random

import memory_defs  # pyright: ignore[reportMissingImports]


class MemoryBlock:
    ALIGN = 64

    def __init__(self, origin=0, size=1024, tipo='ram_le', val=0, desc=''):
        self.origin = origin - (origin % self.ALIGN)
        self.size = size - (size % self.ALIGN)
        self._val = val
        self.desc = desc
        self._tipo = tipo
        self._accesses: dict = {}
        self._data: list[int] = []
        self.set_accesses(tipo)

    def __repr__(self):
        name = memory_defs.MEMORY_NAMES.get(self._tipo, '???')
        return f"{name}: 0x{self.origin:08X} - 0x{self.origin + self.size - 1:08X} # {self.desc}"

    def __str__(self):
        return repr(self)

    # Comparable: blocks are equal when they intersect, less when fully below, greater when fully above
    def cmp_block(self, other: 'MemoryBlock') -> int:
        if other.origin >= self.origin + self.size:
            return -1
        if self.origin >= other.origin + other.size:
            return 1
        return 0

    def cmp(self, address: int) -> int:
        """Return -1/0/1 if address is before/inside/after this block."""
        if address < self.origin:
            return -1
        if address >= self.origin + self.size:
            return 1
        return 0

    def access(self, access_type: str, offset: int, val=None):
        return self._accesses[access_type](self._data, offset, val)

    def fill_from_array(self, data: list) -> 'MemoryBlock':
        self._data = list(data)
        t = len(self._data)
        rm = t % self.ALIGN
        self.size = t if rm == 0 else t + self.ALIGN - rm
        while len(self._data) < self.size:
            self._data.append(0)
        return self

    def fill_from_val(self, val=None) -> 'MemoryBlock':
        if val is None:
            val = self._val
        self._data = [val] * self.size
        return self

    def fill_random(self) -> 'MemoryBlock':
        self._data = [random.randint(0, 255) for _ in range(self.size)]
        return self

    def set_accesses(self, tipo: str) -> None:
        table = memory_defs.MEMORY_TYPES[tipo]
        self._accesses.update(table)

    def reset(self) -> None:
        self._accesses['reset'](self)
