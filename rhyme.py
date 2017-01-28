from grammar_utils import *
from accents import get_accent_position


class MASK_FACTORS:
    PRE_EQUAL = 1.0
    PRE_SIMILAR = 0.9
    PRE_OTHER = 0.8

    ACC_EQUAL = 2.0
    ACC_SIMILAR = 1.9
    ACC_OTHER = 0.5

    POST_EQUAL = 2.0
    POST_SIMILAR = 1.5
    POST_OTHER = 0.5

    TRESHOLD = 3.0


def get_rhyme_mask(word, user_acc_pos=None):
    acc_pos = get_accent_position(
        word) if user_acc_pos is None else user_acc_pos
    if acc_pos is None:
        return None

    vowels_after = 0
    for i in xrange(len(word) - 1, acc_pos, -1):
        if word[i] in VOWELS:
            vowels_after += 1

    pre = word[acc_pos - 1] if acc_pos > 0 else None
    acc = word[acc_pos]
    post = word[acc_pos + 1:] if acc_pos + 1 + \
        2 < len(word) else word[-min(len(word), 2):]

    return vowels_after, pre, acc, post


def compare_masks(mask1, mask2):
    vows1, pre1, acc1, post1 = mask1
    vows2, pre2, acc2, post2 = mask2
    if vows1 != vows2:
        return None

    res = 1.0

    if pre1 == pre2:
        res *= MASK_FACTORS.PRE_EQUAL
    elif pre1 not in VOWELS and pre1 in SIMILAR_CONSONANTS.get(pre2, ()):
        res *= MASK_FACTORS.PRE_SIMILAR
    else:
        res *= MASK_FACTORS.PRE_OTHER

    if acc1 == acc2:
        res *= MASK_FACTORS.ACC_EQUAL
    elif acc1 == SIMILAR_VOWELS.get(acc2):
        res *= MASK_FACTORS.ACC_SIMILAR
    else:
        res *= MASK_FACTORS.ACC_OTHER

    if post1 == post2:
        res *= MASK_FACTORS.POST_EQUAL
    elif post1 is not None and post2 is not None:
        if len(set(post1) & set(post2)) >= max(len(post1), len(post2)) - 1 > 2:
            res *= MASK_FACTORS.POST_SIMILAR
        else:
            for comb, sims in SIMILAR_COMBINATIONS.iteritems():
                if comb in post1:
                    sims1 = [post1.replace(comb, sim) for sim in sims]
                    comps = [len(set(sim1) & set(post2)) >= max(
                        len(sim1), len(post2)) - 1 > 2 for sim1 in sims1]
                    if sum(comps) > 0:
                        res *= MASK_FACTORS.POST_SIMILAR
                        break
            else:
                res *= MASK_FACTORS.POST_OTHER
    else:
        res *= MASK_FACTORS.POST_OTHER

    if res < MASK_FACTORS.TRESHOLD:
        return None
    return res

