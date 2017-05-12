#!/usr/bin/env python2.7

from logging import getLogger
import sys
import Queue as TQueue
from multiprocessing import Process, Queue as RQueue
import time
import requests

import vk

from settings import settings
from sys_utilst import save, get_bar, add_postfix


logger = getLogger(__name__)


def spawn_tasks(task_queue, api, start_id, end_id):
    users = api.groups.getMembers(
        group_id=settings['group_id'], fields='domain')

    items = users['items']
    end_id = min(users['count'] - 1, end_id)
    for task_id in xrange(start_id, end_id):
        user = items[task_id]
        fname = user['first_name']
        lname = user['last_name']
        user_id = user['id']
        if user_id in settings['blacklist']:
            logger.debug('SKIP %d-%s-%s' % (user_id, fname, lname))
            continue

        user_name = '%s %s' % (fname, lname)
        task = {
            'user_id': user_id,
            'user_name': user_name,
            'offset': 0,
            'last': False,
        }

        logger.debug('PUT-%s' % user_name)
        task_queue.put(task)


def process_task(task_queue, api, task):
    max_count = settings['max_post_count']
    count = min(max_count, 100)
    offset = task['offset']

    try:
        posts_data = api.wall.get(
            owner_id=task['user_id'],
            count=count,
            offset=offset,
            filter='owner'
        )

        if not offset:
            next_task = task
            if posts_data['count'] > count:
                while offset < max_count:
                    next_task = dict(task)
                    offset += count
                    next_task['offset'] = offset
                    task_queue.put(next_task)
            next_task['last'] = True

        posts = []
        for post in posts_data['items']:
            text = post.get('text')
            if text:
                posts.append({
                    'text': text,
                    'id': '%d-%d' % (task['user_id'], post['id']),
                    'user_id': task['user_id'],
                })

        return posts

    except vk.exceptions.VkAPIError as error:
        logger.error(error.message)
        if error.code == 6:
            task_queue.put(task)
            return []
    except requests.exceptions.Timeout as error:
        logger.error(error.message)
        task_queue.put(task)
        return []
    except BaseException as error:
        logger.error(error)
        raise


def worker_thread(task_queue, result_queue, api):
    stub_users = set()
    bar = get_bar(max_value=task_queue.qsize())
    bar.update(0)
    last_get_time = time.time()

    def _inc_bar(_progress=[0]):
        _progress[0] += 1
        bar.update(_progress[0])

    while not task_queue.empty():
        task = task_queue.get_nowait()
        user_id = task['user_id']

        if user_id in stub_users:
            continue

        delay = time.time() - last_get_time
        if delay < settings['sleep']:
            time.sleep(settings['sleep'] - delay)

        posts = process_task(task_queue, api, task)
        last_get_time = time.time()

        if posts:
            result_queue.put_nowait(posts)
            if task['last']:
                _inc_bar()
        else:
            stub_users.add(user_id)
            _inc_bar()


def download(start_id, end_id):
    dump_file_name = 'vk_%d_%d.bin' % (start_id, end_id)
    logger.info('download to %s' % dump_file_name)
    session = vk.AuthSession(**settings['bot_auth'])
    api = vk.API(session, lang='en', v='5.45')
    task_queue = TQueue.Queue()
    result_queue = RQueue()
    spawn_tasks(task_queue, api, start_id, end_id)
    worker = Process(target=worker_thread, args=(task_queue, result_queue, api))
    worker.start()

    from normalize import get_normal_sentences
    from rhyme import compare_masks

    last_save_time = time.time()
    mask_to_sentences = {}
    matched_masks = {}
    data = {
        'mask_to_sentences': mask_to_sentences,
        'matched_masks': matched_masks,
    }
    try:
        total_count = 0
        while worker.is_alive() or not result_queue.empty():
            while not result_queue.empty():
                new_masks = set()
                for item in result_queue.get_nowait():
                    for sentence in get_normal_sentences(item):
                        total_count += 1
                        mask = sentence['mask']
                        new_masks.add(mask)
                        mask_to_sentences.setdefault(mask, []).append(sentence)

                real_new_mask = new_masks - set(matched_masks.keys())
                for new_mask in real_new_mask:
                    matched_masks[new_mask] = set()
                    for old_mask in matched_masks.keys():
                        if compare_masks(new_mask, old_mask) is not None:
                            matched_masks.setdefault(
                                new_mask, set()).add(old_mask)
                            matched_masks[old_mask].add(new_mask)

                if time.time() - last_save_time > 5.0:
                    last_save_time = time.time()
                    save(data, add_postfix(dump_file_name, 'tmp'))

        save(data, add_postfix(dump_file_name, 'ext'))
        logger.info('Done %d sentences.' % total_count)

    except KeyboardInterrupt:
        worker.terminate()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        logger.error('Usage: %s id_start id_end' % sys.argv[0])
        sys.exit(42)

    start_id, end_id = [int(i) for i in sys.argv[1:3]]
    download(start_id, end_id)
