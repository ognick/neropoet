# -*- coding: utf-8 -*-

# Read more about:
# http://www.stihi.ru/uchebnik/rifma5.html
from random import choice
import time

import itertools


class RHYME_TYPE:
    ANY = None
    MASCULINE = '*`b'
    FEMALE = '*`bc'
    DACTYLIC = '*`bcd'
    HYPERDACTYLIC = '*`bcde'


_CODE_TO_TYPE = {
    'M'		: RHYME_TYPE.MASCULINE,
    'F'		: RHYME_TYPE.FEMALE,
    'D'		: RHYME_TYPE.DACTYLIC,
    'H'		: RHYME_TYPE.HYPERDACTYLIC,
}

_RHYME_META_TYPE = {}
for k, v in RHYME_TYPE.__dict__.iteritems():
    if k.startswith('_') or not v:
        continue
    min_syllable_count = sum(c.isalpha() for c in v)
    try:
        acc_tail_pos = len(v) - v.index('`') - 2
    except ValueError:
        acc_tail_pos = None

    _RHYME_META_TYPE[v] = (
        sum(c.isalpha() for c in v),  # min syllable in word,
        acc_tail_pos,                 # syllable accents position if defined.
    )

# Rhyme types sequence separated by space.
# RHYME_TYPE [:SIZE] [:MAX_DELTA]
# DEFAULT VALUES:
#   SIZE = ANY
#   MAX_DELTA = 0


class RHYME_SYSTEM:
    # PLAIN = 'A A B B'
    # INTERLACED = 'A B A B'
    # ENCLOSING = 'A B B A'
    # CROSSED = 'A B C A B C'
    # CUSTOM = 'M:10:2 F:10:2 M:10:2 F:10:2'
    PLAIN6 = 'A:6:1 A:6:1 B:6:1 B:6:1'
    PLAIN7 = 'A:7:1 A:7:1 B:7:1 B:7:1'
    PLAIN8 = 'A:8:1 A:8:1 B:8:1 B:8:1'

    INTERLACED6 = 'A:6:1 B:6:1 A:6:1 B:6:1'
    INTERLACED7 = 'A:7:1 B:7:1 A:7:1 B:7:1'
    INTERLACED8 = 'A:8:1 B:8:1 A:8:1 B:8:1'




def detect_rhyme_type(mask):
    vowels_after = mask[0]
    for rhyme_type, (min_syllable, acc_tail_pos) in _RHYME_META_TYPE.iteritems():
        if acc_tail_pos == vowels_after:
            return rhyme_type
    return RHYME_TYPE.ANY


def parse_rhyme_system(rhyme_system):
    type_to_lens = {}
    unique_types = []
    pure_rhyme_system = []
    for s in rhyme_system.split():
        parts = s.split(':')
        rhyme_type, length, max_delta = parts + ['A', 0, None][len(parts):]
        if rhyme_type not in unique_types:
            unique_types.append(rhyme_type)
        if max_delta:
            max_delta = int(max_delta)
        type_to_lens.setdefault(rhyme_type, []).append(
            (int(length), max_delta))
        pure_rhyme_system.append(rhyme_type)
    return pure_rhyme_system, type_to_lens, unique_types
