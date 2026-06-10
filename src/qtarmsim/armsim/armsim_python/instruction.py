# -*- coding: utf-8 -*-

import thumb2_defs as T  # pyright: ignore[reportMissingImports]


class Instruction:
    """Decoded ARM Thumb-II instruction with type, operands, and word(s)."""

    def __init__(self, words: list, address: int | None = None):
        self.words = words
        self._address = address
        self._type: str = ''
        self.size: int = 1
        self.operands: list = []

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, it: str) -> None:
        self._type = it
        self.size = T.SET[it][4]
        if self.size == 1:
            self.words = self.words[0]
        else:
            self.words = self.words[:self.size]

    def to_s(self) -> str:
        return T.instr_to_s(self._type, self.operands, self._address or 0)

    def kind(self) -> str:
        return T.SET[self._type][1]

    def execute(self, estado: dict) -> dict:
        data = T.prep_data(self._type, self.operands, estado)
        return T.execute(self._type, data)
