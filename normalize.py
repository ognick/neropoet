from logging import getLogger
from rhyme import get_rhyme_mask
from w2v_model import extract_key_words
from grammar_utils import *


logger = getLogger(__name__)


def get_normal_sentences(post):
    text = post['text']

    if text is None:
        return []

    for c in SPLITS + ENDS:
        text = text.replace(c, c + '|')

    sentences = [s for s in text.split('|') if has_russian_chars(s)]
    long_sentences = []
    for pos, sentence in enumerate(sentences):
        if 0 < get_length(sentence) < 5:
            if pos > 0:
                long_sentences.append(sentences[pos - 1] + sentence)

            if pos < len(sentences) - 2:
                long_sentences.append(sentence + sentences[pos + 1])

    norm_sentences = []
    for sentence in set(sentences + long_sentences):
        sentence = sentence.strip()
        sentence = sentence[0].upper() + sentence[1:]
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

        key_words = extract_key_words(words)
        if not key_words:
            continue

        newItem = dict(post)
        newItem.update({
            'text': sentence,
            'id': '%s-%d' % (post['id'], i),
            'words': normalize_sentence(sentence),
            'norm': norm,
            'length': length,
            'last_word': last_word,
            'mask': mask,
            'key_words': key_words,
        })
        sentences.append(newItem)

    return sentences
