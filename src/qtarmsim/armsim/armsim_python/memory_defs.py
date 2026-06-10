# -*- coding: utf-8 -*-
# Memory access function tables for ARM simulator.
# Error sentinels are strings: 'errnoalign', 'errnoblock'


def read_byte(data, offset, _val=None):
    return data[offset]


def read_half_le(data, offset, _val=None):
    if offset & 1:
        return 'errnoalign'
    return (data[offset] | (data[offset + 1] << 8)) & 0xFFFF


def read_half_le_na(data, offset, _val=None):
    return (data[offset] | (data[offset + 1] << 8)) & 0xFFFF


def read_half_be(data, offset, _val=None):
    if offset & 1:
        return 'errnoalign'
    return (data[offset + 1] | (data[offset] << 8)) & 0xFFFF


def read_word_le(data, offset, _val=None):
    if offset & 3:
        return 'errnoalign'
    return (data[offset] | (data[offset + 1] << 8) |
            (data[offset + 2] << 16) | (data[offset + 3] << 24)) & 0xFFFFFFFF


def read_word_le_na(data, offset, _val=None):
    return (data[offset] | (data[offset + 1] << 8) |
            (data[offset + 2] << 16) | (data[offset + 3] << 24)) & 0xFFFFFFFF


def read_word_be(data, offset, _val=None):
    if offset & 3:
        return 'errnoalign'
    return (data[offset + 3] | (data[offset + 2] << 8) |
            (data[offset + 1] << 16) | (data[offset] << 24)) & 0xFFFFFFFF


def write_byte(data, offset, byte):
    data[offset] = byte & 0xFF
    return 0


def write_half_le(data, offset, half):
    data[offset] = half & 0xFF
    data[offset + 1] = (half >> 8) & 0xFF
    return 'errnoalign' if offset & 1 else 0


def write_half_le_na(data, offset, half):
    data[offset] = half & 0xFF
    data[offset + 1] = (half >> 8) & 0xFF
    return 0


def write_half_be(data, offset, half):
    data[offset + 1] = half & 0xFF
    data[offset] = (half >> 8) & 0xFF
    return 'errnoalign' if offset & 1 else 0


def write_word_le(data, offset, word):
    data[offset] = word & 0xFF
    data[offset + 1] = (word >> 8) & 0xFF
    data[offset + 2] = (word >> 16) & 0xFF
    data[offset + 3] = (word >> 24) & 0xFF
    return 0 if (offset & 3) == 0 else 'errnoalign'


def write_word_le_na(data, offset, word):
    data[offset] = word & 0xFF
    data[offset + 1] = (word >> 8) & 0xFF
    data[offset + 2] = (word >> 16) & 0xFF
    data[offset + 3] = (word >> 24) & 0xFF
    return 0


def write_word_be(data, offset, word):
    data[offset + 3] = word & 0xFF
    data[offset + 2] = (word >> 8) & 0xFF
    data[offset + 1] = (word >> 16) & 0xFF
    data[offset] = (word >> 24) & 0xFF
    return 0 if (offset & 3) == 0 else 'errnoalign'


def nothing(data, offset, val):
    return 0


def nothing_h(data, offset, val):
    return 0 if (offset & 1) == 0 else 'errnoalign'


def nothing_w(data, offset, val):
    return 0 if (offset & 3) == 0 else 'errnoalign'


def ram_reset(block):
    block.fill_from_val()


def rom_reset(block):
    pass


RAM_LE = {
    'rb': read_byte, 'rh': read_half_le, 'rw': read_word_le,
    'wb': write_byte, 'wh': write_half_le, 'ww': write_word_le,
    'reset': ram_reset,
}

RAM_LE_NA = {
    'rb': read_byte, 'rh': read_half_le_na, 'rw': read_word_le_na,
    'wb': write_byte, 'wh': write_half_le_na, 'ww': write_word_le_na,
    'reset': ram_reset,
}

ROM_LE = {
    'rb': read_byte, 'rh': read_half_le, 'rw': read_word_le,
    'wb': nothing, 'wh': nothing_h, 'ww': nothing_w,
    'reset': rom_reset,
}

RAM_BE = {
    'rb': read_byte, 'rh': read_half_be, 'rw': read_word_be,
    'wb': write_byte, 'wh': write_half_be, 'ww': write_word_be,
    'reset': ram_reset,
}

ROM_BE = {
    'rb': read_byte, 'rh': read_half_be, 'rw': read_word_be,
    'wb': nothing, 'wh': nothing_h, 'ww': nothing_w,
    'reset': rom_reset,
}

MEMORY_TYPES = {
    'ram_le': RAM_LE, 'rom_le': ROM_LE,
    'ram_be': RAM_BE, 'rom_be': ROM_BE,
}

MEMORY_NAMES = {
    'ram_le': 'RAM', 'rom_le': 'ROM',
    'ram_be': 'RAM', 'rom_be': 'ROM',
}
