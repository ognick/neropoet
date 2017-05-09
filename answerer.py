#!/usr/bin/env python2.7
# -*- coding: utf-8


import time
import sys
from logging import getLogger
import requests
import json
import vk
from settings import settings
from sys_utilst import load, save
from grammar_utils import normalize_sentence
from w2v_model import in_vocab
from pictures.generator import generate_image
from style import RHYME_SYSTEM
from poet import build


logger = getLogger(__name__)


MAX_USERS_PER_REQUEST = 1000
MAX_MESSAGES_PER_REQUEST = 200

NOT_FOLLOW_MSG = u'Сначала вступи в этот паблик.'
BAD_WORDS_MSG= u'Я таких слов не знаю.'
NO_BLOCKS_MSG=u'Что-то об этом мало пишут.'


def get_all_items(max_count_per_request, getter):
    total_count = max_count_per_request
    offset = 0
    items = []
    while offset < total_count:
        response = getter(offset=offset, count=max_count_per_request)
        items.extend(i for i in response['items'])
        total_count = response['count']
        offset += MAX_USERS_PER_REQUEST
        time.sleep(settings['sleep'])

    return items


def answer(source_file_name):
    try:
        used_cache = load('used_cache.bin')
    except IOError:
        used_cache = {}

    data = load(source_file_name)
    mask_to_sentences = data['mask_to_sentences']
    matched_masks = data['matched_masks']
    system = RHYME_SYSTEM.CAKE

    session = vk.Session(settings['group_token'])
    api = vk.API(session, lang='ru', v='5.64')

    followers = get_all_items(
        MAX_USERS_PER_REQUEST,
        lambda **kwargs : api.groups.getMembers(group_id=settings['group_id'], fields='domain', **kwargs)
    )
    followers = {u['id']: '%s %s' % (u['first_name'], u['last_name']) for u in followers}

    messages = get_all_items(
        MAX_MESSAGES_PER_REQUEST,
        lambda **kwargs : api.messages.getDialogs(unanswered=1, preview_length=20, **kwargs)
    )

    def _answer(uid, sign, post, title):
        logger.info('sending to %s %s' % (sign, title))
        # if uid not in settings['tester_ids']:
        #     return

        generate_image(post, sign=sign, title=title, result_file='img.jpg')
        img = {'photo': ('img.png', open(r'img.jpg', 'rb'))}
        upload_url = api.photos.getMessagesUploadServer()['upload_url']
        response = json.loads(requests.post(upload_url, files=img).text)

        photo_data = api.photos.saveMessagesPhoto(photo=response['photo'],
                                                  hash=response['hash'],
                                                  server=response['server'])

        attach = 'photo%s_%s' % (photo_data[0]['owner_id'], photo_data[0]['id'])
        api.messages.send(user_id=uid, attachment=[attach])
        time.sleep(settings['sleep'])

    for item in messages:
        msg = item['message']
        user_id = msg['user_id']

        # if user_id not in settings['tester_ids']:
        #     continue

        init_sign = followers.get(user_id)
        if not init_sign:
            api.messages.send(user_id=user_id, message=NOT_FOLLOW_MSG)
            time.sleep(settings['sleep'])
            continue

        words = normalize_sentence(msg['body'])
        logger.info('words %s' % ' '.join(words))
        good_words = set([w for w in words if in_vocab(w)])
        if len(good_words) != 1:
            api.messages.send(user_id=user_id, message=BAD_WORDS_MSG)
            time.sleep(settings['sleep'])
            continue

        title = ' '.join(good_words)
        logger.info('good words %s' % title)
        blocks = build(mask_to_sentences, matched_masks, system, good_words)
        if not blocks:
            api.messages.send(user_id=user_id, message=NO_BLOCKS_MSG)
            time.sleep(settings['sleep'])
            continue

        curr_user_cache = used_cache.setdefault(user_id, set())
        while blocks:
            block = blocks.pop()
            post = []
            is_author = {user_id: True}

            for sentence in block:
                post.append(sentence['text'])
                author_id = sentence['user_id']
                if author_id in followers:
                    is_author[author_id] = True

            s_post = set(post)
            if curr_user_cache & s_post:
                continue

            is_author.update({uid: False for uid in settings['tester_ids']})
            for user_id, is_cached in is_author.iteritems():
                if is_cached:
                    user_cache = used_cache.setdefault(user_id, set())
                    if user_cache & s_post:
                        continue

                try:
                    sign = followers[user_id] if is_cached else init_sign
                    _answer(user_id, sign, post, title)
                    if is_cached:
                        user_cache |= s_post
                        save(used_cache, 'used_cache.bin')
                except vk.exceptions.VkAPIError as error:
                    logger.error('%s %s' %(sign, error.message))
                    continue
            break
        else:
            api.messages.send(user_id=user_id, message=NO_BLOCKS_MSG)
            time.sleep(settings['sleep'])

    return 0


if __name__ == '__main__':
    sys.exit(answer(sys.argv[1]))
