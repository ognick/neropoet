#!/usr/bin/env python2.7
# -*- coding: utf-8

import sys
from logging import getLogger
from settings import settings
from sys_utilst import load, get_bar, save, change_postfix
from style import parse_rhyme_system, RHYME_SYSTEM
from grammar_utils import *


logger = getLogger(__name__)


def build(mask_to_sentences, matched_masks, rhyme_system, init_words):
    from w2v_model import in_vocab, n_similarity
    init_words = set([w for w in init_words if in_vocab(w)])
    if not init_words:
        logger.error('init words there are not in vocab')
        return []

    logger.info('init words: %s' % ', '.join(init_words))

    def _get_nearest_word(s):
        similar = best_key_word = None
        for word in s['key_words']:
            cur_similar = n_similarity(init_words, word)
            if cur_similar > similar:
                similar = cur_similar
                best_key_word = word
        return (similar, best_key_word)

    rhyme_system, type_to_lens, unique_types = parse_rhyme_system(rhyme_system)
    [(ln1, d1), (ln2, d2)] = [type_to_lens[t][0] for t in unique_types]

    similarities = {}
    all_masks = matched_masks.keys()
    logger.info('matching key words. %d masks' % len(all_masks))
    bar = get_bar(max_value=len(all_masks))
    for mi, mask in enumerate(all_masks):
        sentences = []
        for m in matched_masks[mask]:
            sentences.extend(mask_to_sentences[m])

        for i, s1 in enumerate(sentences):
            if ln1 and abs(s1['length'] - ln1) > d1:
                continue

            similar1, s1['best_word'] = _get_nearest_word(s1)
            if similar1 < settings['similarity_threshold']:
                continue

            s1['similar'] = similar1
            last_word_s1 = s1['last_word']
            cur_similarities = {}
            similarities.setdefault(similar1, []).append(
                (s1, cur_similarities))

            for j in xrange(0, len(sentences)):
                s2 = sentences[j]

                if ln2 and abs(s2['length'] - ln2) > d2:
                    continue

                last_word_s2 = s2['last_word']
                if last_word_s2.find(last_word_s1) != -1 or last_word_s1.find(last_word_s2) != -1:
                    continue

                if WORD_TO_GROUP.get(last_word_s1, 0) == WORD_TO_GROUP.get(last_word_s2, 1):
                    continue

                if is_conjugate_words(last_word_s1, last_word_s2):
                    continue

                similar2, s2['best_word'] = _get_nearest_word(s2)
                if similar2 < settings['similarity_threshold']:
                    continue

                s2['similar'] = similar2

                cur_similarities.setdefault(similar2, []).append(s2)

        bar.update(mi)
    logger.info('matching key words done.')

    pairs = []
    logger.info('joining flatten list.')
    for sim1 in sorted(similarities.keys(), reverse=True):
        for s1, sim2_to_words in similarities[sim1]:
            for sim2 in sorted(sim2_to_words.keys(), reverse=True):
                pairs.extend([[s1, s2] for s2 in sim2_to_words[sim2]])

    for pair in pairs:
        assert pair

    logger.info('joining flatten list %d pairs done.' % len(pairs))

    g_used = set()
    def _is_good(l_used, pair):
        if not pair:
            return False

        for p in pair:
            if p['norm'] in g_used or p['last_word'] in l_used or p['best_word'] in l_used:
                return False

        for p in pair:
            l_used.add(p['last_word'])
            l_used.add(p['best_word'])
        return True

    def _add_to_g_used(pairs):
        for pair in pairs:
            for p in pair:
                g_used.add(p['norm'])

    blocks = []
    logger.info('building blocks.')
    rt1, rt2 = unique_types
    for i, pair1 in enumerate(pairs):
        if len(blocks) >= settings['max_block_count']:
            logger.info('building blocks %d done.' % len(blocks))
            return blocks

        try:
            l_used = set()
            if not _is_good(l_used, pair1):
                continue

            for j, pair2 in enumerate(pairs):
                if _is_good(l_used, pair2):
                    _add_to_g_used([pair1, pair2])
                    rt2pairs = {rt1: pair1, rt2: pair2}
                    block = []
                    for rt in rhyme_system:
                        block.append(rt2pairs[rt].pop(0))
                    blocks.append(block)
                    raise StopIteration
        except StopIteration:
            continue

    logger.info('building blocks %d done.' % len(blocks))
    return blocks


def main():
    if len(sys.argv) < 3:
        print 'Usage: %s filename.bin [init_word]+' % sys.argv[0]
        exit(42)

    file_name = sys.argv[1]
    data = load(file_name)
    mask_to_sentences = data['mask_to_sentences']
    matched_masks = data['matched_masks']
    system = RHYME_SYSTEM.CAKE
    init_words = [w.decode('utf-8') for w in sys.argv[2:]]
    blocks = build(mask_to_sentences, matched_masks, system, init_words)
    for block in blocks:
        for line in block:
            print line['text']
        print
    save(blocks, change_postfix(file_name, 'out'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
