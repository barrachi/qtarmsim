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

# =========================================================================
#  References:
#   http://doc.qt.io/qt-5/qtwidgets-richtext-syntaxhighlighter-example.html
# =========================================================================

from PySide6 import QtGui

from .commonsyntaxhighlighter import HighlightingRule, CommonSyntaxHighlighter


def generateCHighlightingRules():
    #
    # The following keywords have been obtained from the KDE syntax-highlight framework (c syntax):
    #   https://github.com/KDE/syntax-highlighting/blob/master/data/syntax/c.xml
    #
    control_flow = """
        break,
        case,
        continue,
        default,
        do,
        else,
        for,
        goto,
        if,
        return,
        switch,
        while
    """
    keywords = """
        enum,
        extern,
        inline,
        sizeof,
        struct,
        typedef,
        union,
        _Alignas,
        _Alignof,
        _Atomic,
        _Noreturn,
        _Static_assert,
        _Thread_local
    """
    types = """
        auto,
        char,
        const,
        double,
        float,
        int,
        long,
        register,
        restrict,
        short,
        signed,
        static,
        unsigned,
        void,
        volatile,
        int8_t,
        int16_t,
        int32_t,
        int64_t,
        uint8_t,
        uint16_t,
        uint32_t,
        uint64_t,
        int_least8_t,
        int_least16_t,
        int_least32_t,
        int_least64_t,
        uint_least8_t,
        uint_least16_t,
        uint_least32_t,
        uint_least64_t,
        int_fast8_t,
        int_fast16_t,
        int_fast32_t,
        int_fast64_t,
        uint_fast8_t,
        uint_fast16_t,
        uint_fast32_t,
        uint_fast64_t,
        size_t,
        ssize_t,
        wchar_t,
        intptr_t,
        uintptr_t,
        intmax_t,
        uintmax_t,
        ptrdiff_t,
        sig_atomic_t,
        wint_t,
        _Bool,
        bool,
        _Complex,
        complex,
        _Imaginary,
        imaginary,
        _Generic,
        va_list,
        FILE,
        fpos_t,
        time_t,
        max_align_t
    """
    highlightingRules = []
    # Add highlighting rules and format for C control flow directives
    controlFlowFormat = QtGui.QTextCharFormat()
    controlFlowFormat.setForeground(QtGui.QColor('black'))
    controlFlowFormat.setFontWeight(QtGui.QFont.Bold)
    pattern = '({})\\b'.format('|'.join(control_flow.replace('\n', '').replace(' ', '').replace('.', '').split(',')))
    highlightingRules.append(HighlightingRule(pattern, controlFlowFormat))
    # Add highlighting rules and format for C keywords
    keywordsFormat = QtGui.QTextCharFormat()
    keywordsFormat.setForeground(QtGui.QColor('darkBlue'))
    keywordsFormat.setFontWeight(QtGui.QFont.Bold)
    pattern = '({})\\b'.format('|'.join(keywords.replace('\n', '').replace(' ', '').replace('.', '').split(',')))
    highlightingRules.append(HighlightingRule(pattern, keywordsFormat))
    # Add highlighting rules and format for C types
    typesFormat = QtGui.QTextCharFormat()
    typesFormat.setForeground(QtGui.QColor('darkBlue'))
    pattern = '({})\\b'.format('|'.join(types.replace('\n', '').replace(' ', '').replace('.', '').split(',')))
    highlightingRules.append(HighlightingRule(pattern, typesFormat))
    # Add highlighting rules and format for numbers
    numbersFormat = QtGui.QTextCharFormat()
    numbersFormat.setForeground(QtGui.QColor('darkOrange'))
    pattern = '\\b[0-9]+\\b'
    highlightingRules.append(HighlightingRule(pattern, numbersFormat))
    # Add highlighting rules and format for #define
    defineFormat = QtGui.QTextCharFormat()
    defineFormat.setForeground(QtGui.QColor('green'))
    pattern = '#define.*$'
    highlightingRules.append(HighlightingRule(pattern, defineFormat))
    # Add highlighting rules and format for C comments
    commentsFormat = QtGui.QTextCharFormat()
    commentsFormat.setForeground(QtGui.QColor('gray'))
    pattern = '//.*$'
    highlightingRules.append(HighlightingRule(pattern, commentsFormat))
    return highlightingRules


class CSyntaxHighlighter(CommonSyntaxHighlighter):
    """Class that can be used to parse and highlight C assembler code"""

    def __init__(self, parent):
        """Initializes the different patterns and their respective formats"""
        super().__init__(parent)
        self.highlightingRules = generateCHighlightingRules()
