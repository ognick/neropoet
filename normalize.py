from logging import getLogger
from rhyme import get_rhyme_mask
from w2v_model import extract_key_words
from grammar_utils import *


logger = getLogger(__name__)


def get_normal_sentences(post):
    text = post['text']

    if text is None:
        return []

    for c in frozenset(']}>\n') | ENDS:
        text = text.replace(c, c + '|')

    for c in frozenset([' - ']):
        text = text.replace(c, '|')

    sentences = [s for s in text.split('|') if has_russian_chars(s) and 0 < len(s) < 40]
    long_sentences = []
    for pos, sentence in enumerate(sentences):
        if get_length(sentence) < 6:
            if pos > 0:
                long_sentences.append(sentences[pos - 1] + sentence)

            if pos < len(sentences) - 2:
                long_sentences.append(sentence + sentences[pos + 1])

    norm_sentences = []
    for sentence in set(sentences + long_sentences):
        sentence = sentence.strip()
        sentence = list(sentence)
        sentence[0] = sentence[0].upper()
        sentence = ''.join(sentence)
        sentence = ' '.join(sentence.split())
        if sentence[-1] not in ENDS:
            sentence += '.'
        norm_sentences.append(sentence)

    sentences = []
    for i, sentence in enumerate(norm_sentences):
        words = normalize_sentence(sentence)
        norm = ' '.join(words)
        length = get_length(norm)
        if length < 3 or length > 16:
            continue

        last_word = words[-1]
        if last_word in BAD_ENDINGS:
            continue

        mask = get_rhyme_mask(last_word)
        if not mask:
            continue

        last_word, morphy_tag = try_normalize_word(last_word)
        if not morphy_tag:
            continue

        key_words = extract_key_words([try_normalize_word(w)[0] for w in words])
        if not key_words:
            continue

        newItem = dict(post)
        newItem.update({
            'text': sentence,
            'id': '%s-%d' % (post['id'], i),
            'words': words,
            'norm': norm,
            'length': length,
            'last_word': last_word,
            'mask': mask,
            'key_words': key_words,
            'morphy_tag': morphy_tag,
        })
        sentences.append(newItem)

    return sentences