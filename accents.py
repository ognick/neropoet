#!/usr/bin/env python2.7
# -*- coding: utf-8

import time
import codecs
import logging

from grammar_utils import *


_ACCENT_BOOKS = ('accents_total.txt', 'accents_ru_noun.txt')

_g_accents = {}           # word => accent position
_g_syllable_accents = {}  # word => accent position by syllable


def _load_accent_books():
    t = time.time()
    for book in _ACCENT_BOOKS:
        with codecs.open('dictionary/' + book, 'r', 'utf-8') as f:
            lines = f.read().split('\n')
            for line in lines:
                try:
                    line = line.strip()
                    acc = line.index('`')
                    line = line.replace('`', '')
                    if line in _g_accents:
                        continue
                    _g_accents[line] = acc

                    total_syllables = 0
                    acc_syllable = None
                    for pos, l in enumerate(line):
                        if acc_syllable is None and pos == acc:
                            acc_syllable = total_syllables
                        if l in VOWELS:
                            total_syllables += 1
                    _g_syllable_accents[line] = (acc_syllable, total_syllables)
                except:
                    pass

    logging.debug('finished loading accent books (%d words in %.2f seconds)' % (
        len(_g_accents), time.time() - t))


_load_accent_books()


def get_accent_position(word):
    n = 0
    wi = 0
    for pos, l in enumerate(word):
        if l in VOWELS:
            n += 1
            wi = pos
    if n == 0:
        return None
    if n == 1:
        return wi
    return _g_accents.get(word, None)


def get_back_syllable_accent(word):
    acc_syllable, total_syllables = _g_syllable_accents[word]
    return total_syllables - acc_syllable - 1
