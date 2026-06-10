# -*- coding: utf-8 -*-

from . import thumb2_defs as T

from .instruction import Instruction
from .memory import Memory
from .memory_block import MemoryBlock


class Core:
    """ARM Thumb-II processor core: registers, flags, memory, and execution."""

    def __init__(self, arch: str, block=None):
        self.arch = arch
        if block is None:
            memoria = Memory(0x10000000, 1024, 0, 'Data RAM')
        else:
            memoria = Memory(block)
        self._estado = T.reset()
        self._estado['memory'] = memoria

    def execute(self, inst: Instruction) -> dict:
        res = inst.execute(self._estado)
        if res.get('usr_regs') is None:
            res['usr_regs'] = [T.PC, self._estado['usr_regs'][T.PC] + 2 * inst.size]
        else:
            # Check whether PC is already in the result
            haypc = False
            regs = res['usr_regs']
            num_pairs = len(regs) // 2
            for idx in range(num_pairs):
                if regs[2 * idx] == T.PC:
                    haypc = True
                    break
            if not haypc:
                res['usr_regs'].append(T.PC)
                res['usr_regs'].append(self._estado['usr_regs'][T.PC] + 2 * inst.size)
        res = self.update(res)
        return res

    def update(self, data: dict) -> dict:
        if data.get('usr_regs') is not None:
            regs = data['usr_regs']
            num_pairs = len(regs) // 2
            for ind in range(num_pairs):
                self._estado['usr_regs'][regs[2 * ind]] = regs[2 * ind + 1] & 0xFFFFFFFF

        if data.get('flags') is not None:
            for key, val in data['flags'].items():
                self._estado['flags'][key] = val

        if data.get('memory') is not None:
            access_type = data['memory'][0]
            pairs = data['memory'][1]
            for idx, pair in enumerate(pairs):
                acok = self._estado['memory'].access(access_type, pair[0], pair[1])
                if isinstance(acok, str):
                    data['error'] = [acok, pair[0]]
                    if idx == 0:
                        del data['memory']
                    else:
                        data['memory'][1] = pairs[:idx]
                    break

        return data

    def memory(self) -> Memory:
        return self._estado['memory']

    def reg(self, num: int) -> int:
        return self._estado['usr_regs'][num]

    def flag(self, sym: str) -> int:
        return self._estado['flags'][sym]

    def flags(self) -> dict:
        return self._estado['flags']

    def memory_byte(self, address: int):
        return self._estado['memory'].access('rb', address)

    def memory_half(self, address: int):
        return self._estado['memory'].access('rh', address)

    def memory_word(self, address: int):
        return self._estado['memory'].access('rw', address)
