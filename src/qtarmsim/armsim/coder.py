# -*- coding: utf-8 -*-
from . import thumb2_defs as T
from .instruction import Instruction


class Coder:
    """Decodes 16/32-bit Thumb-II words into Instruction objects."""

    def decode(self, words: list, address: int | None = None) -> Instruction:
        inst = Instruction(words, address)
        tipo = self.get_type(words)
        if tipo is None:
            tipo = 'udef'
        inst.type = tipo
        inst.operands = self.get_operands(words, tipo)
        return inst

    def get_type(self, words: list) -> str | None:
        lista = T.MAINOPC
        res = 0
        size = 0
        word = 0

        while lista[1] != 0:
            if size != lista[4]:
                size = lista[4]
                word = 0
                for idx in range(size):
                    word = (word << 16) + words[idx]

            opcode = T.to_bin(T.valor_campo(word, lista[2]), lista[1])
            sublist = lista[3]

            matched = False
            for elemento in sublist:
                res = T.compara_bin(opcode, elemento[0])
                if res == 1:
                    continue      # not reached this element yet
                if res == -1:
                    return None   # past all candidates
                # res == 0: match
                if elemento[1] == 0:
                    return elemento[2]   # terminal: return instruction type
                lista = elemento
                matched = True
                break

            if not matched and res == 1:
                return None

        return None

    def get_operands(self, words: list, tipo: str) -> list:
        entry = T.SET[tipo]
        size = entry[4]
        word = 0
        for idx in range(size):
            word = (word << 16) + words[idx]
        result = []
        for i, mask in enumerate(entry[3]):
            result.append(T.valor_campo(word, mask, entry[2][i]))
        return result
