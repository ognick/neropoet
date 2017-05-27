# -*- coding: utf-8

import re
import pymorphy2

_g_MorphAnalyzer = None
_g_norm_cache = {}
_INVALID_CHARS = re.compile(ur'[^a-zA-Zа-яёЁА-Я0-9]', re.UNICODE)
_RUSSIAN_VOWELS_RE = re.compile(ur'[ауоыиэяюёе]', re.UNICODE)

VOWELS = set(u'аёеиоуэыюяaeioquy')

SAME_WORDS = [
    [u'тебе', u'себе', u'мне'],
    [u'тебя', u'себя', u'я', u'меня'],
    [u'вас', u'нас'],
    [u'и', u'ли'],
    [u'же', u'уже'],
    [u'итак', u'так'],
    [u'то', u'того', u'зато', u'всё', u'что', u'всего',
        u'чего', u'оттого', u'отчего', u'ничего'],
    [u'ты', u'вы', u'мы'],
    [u'мой', u'твой', u'свой'],
    [u'моего', u'твоего', u'своего', u'его'],
    [u'туда', u'куда'],
    [u'так', u'как'],
]


WORD_TO_GROUP = {}
for i, g in enumerate(SAME_WORDS):
    for w in g:
        WORD_TO_GROUP[w] = i


BAD_ENDINGS = {
    u'бы', u'же', u'на', u'ну',
    u'того', u'том', u'его', u'нет',
    u'но', u'всё', u'все', u'да', u'ему',
    u'то', u'чем', u'всем',
}

ENDS = frozenset('.,:?!)')

NUMBERS = {
    u'0': u' ноль',
    u'1': u' один',
    u'2': u' два',
    u'3': u' три',
    u'4': u' четыре',
    u'5': u' пять',
    u'6': u' шесть',
    u'7': u' семь',
    u'8': u' восеьм',
    u'9': u' девять',
}

SIMILAR_VOWELS = {
    u'a': u'я', u'е': u'э', u'ё': u'о', u'и': u'ы',
    u'о': u'ё', u'у': u'ю', u'ы': u'и', u'э': u'е',
    u'ю': u'у', u'я': u'а'
}

SIMILAR_CONSONANTS = {
    u'б': (u'п',), u'в': (u'ф',), u'г': (u'к', u'х'), u'д': (u'т',),
    u'ж': (u'ш',), u'з': (u'c',), u'к': (u'г', u'х'), u'л': (u'м', u'н'),
    u'м': (u'н', u'л'), u'н': (u'м', u'л'), u'п': (u'б',), u'р': (),
    u'с': (u'з', u'ц'), u'т': (u'д',), u'ф': (u'в',), u'х': (u'к', u'г'),
    u'ц': (u'с',), u'ч': (u'щ',), u'ш': (u'щ',), u'щ': (u'ч', u'ш',)
}

SIMILAR_COMBINATIONS = {
    u'ца': (u'ться', u'тся'), u'ться': (u'тся', u'ца'),
    u'тся': (u'ться', u'ца'),
    u'ых': (u'ах',), u'ах': (u'ых',),
    u'ы': (u'а',), u'а': (u'ы',),
    u'о': (u'a',), u'a': (u'о',),
    u'е': (u'и'), u'и': (u'е', u'ой'), u'ой': (u'и'),
}


VERBS = frozenset(['VERB', 'INFN'])
NPRO = frozenset(['NPRO'])
ADJF = frozenset(['ADJF'])
BAD_END_TAGS = NPRO | ADJF


def convert_numbers(text):
    for k, v in NUMBERS.iteritems():
        text = text.replace(k, v)
    return text


def get_length(text):
    text = convert_numbers(text)
    return sum([c in VOWELS for c in text])


def normalize_sentence(text):
    text = _INVALID_CHARS.sub(' ', text.lower())
    return text.split()


def has_russian_chars(text):
    return bool(_RUSSIAN_VOWELS_RE.search(text))


def try_normalize_word(word):
    res = _g_norm_cache.get(word, None)
    if res is not None:
        return res

    global _g_MorphAnalyzer
    if _g_MorphAnalyzer is None:
        _g_MorphAnalyzer = pymorphy2.MorphAnalyzer()
    parse_results = _g_MorphAnalyzer.parse(word)
    if not parse_results:
        return word, frozenset()

    res = (parse_results[0].normal_form, parse_results[0].tag.grammemes)
    _g_norm_cache[word] = res

    return res