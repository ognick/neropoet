from logging import getLogger

import word2vec
import numpy as np


logger = getLogger(__name__)


logger.debug('loading...')
_g_w2v_model = word2vec.load('dictionary/wiki-model.bin')
logger.debug('loaded done.')


def in_vocab(word):
    return word in _g_w2v_model


def n_similarity(words, word):
    metrics = np.dot([_g_w2v_model[w] for w in words], _g_w2v_model[word].T)
    return sum(metrics) / float(len(metrics))


def extract_key_words(words):
    return set(word for word in words if word in _g_w2v_model)
