# -*- coding: utf-8 -*-
from .memory_block import MemoryBlock


class Memory:
    def __init__(self, origin_or_block=0, size=1024, val=0, desc='Main memory'):
        if isinstance(origin_or_block, MemoryBlock):
            b = origin_or_block
        else:
            b = MemoryBlock(origin_or_block, size, 'ram_le', val, desc)
            b.fill_from_val()
        self._data: list[MemoryBlock] = [b]
        self.symbol_table: dict | None = None

    def __str__(self):
        return '\r\n'.join(str(b) for b in self._data) + '\r\n'

    def add_block(self, block: MemoryBlock):
        for b in self._data:
            if b.cmp_block(block) == 0:
                return None
        self._data.append(block)
        self._data.sort(key=lambda b: b.origin)
        return block

    def find_block(self, address: int):
        for b in self._data:
            d = b.cmp(address)
            if d == 0:
                return b
            if d < 0:
                return None
        return None

    def access(self, access_type: str, address: int, data=None):
        b = self.find_block(address)
        if b is None:
            return 'errnoblock'
        return b.access(access_type, address - b.origin, data)

    def reset(self) -> None:
        for b in self._data:
            b.reset()
