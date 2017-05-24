#!/usr/bin/env python2.7

import time
import sched
import sys

from multiprocessing import Process
from logging import getLogger
from settings import settings
from sys_utilst import is_exists

logger = getLogger('autorun')

start_id = int(sys.argv[1])
end_id = int(sys.argv[2])
file_name = 'vk_%s_%s_ext.bin' % (start_id, end_id)
logger.info(file_name)

class ACTION:
    RELOAD = 1
    ANSWER = 2
    RANGE = (ANSWER, RELOAD)


ACTION_NAMES = dict(
    [(v, k) for k, v in ACTION.__dict__.iteritems() if not k.startswith('_')])


DELAY = {
    ACTION.ANSWER: settings['answer'],
    ACTION.RELOAD: settings['reload'],
}


def plan(action):
    scheduler.enter(DELAY[action], 1, TODO[action], (action,))


def reschedule(f):
    def wrap(action):
        try:
            f()
        except BaseException as e:
            logger.error('SKIP %s %s' % (ACTION_NAMES[action], e))
        plan(action)
    return wrap


@reschedule
def do_answer():
    if is_exists(file_name):
        from answerer import loop
        loop(file_name)

@reschedule
def do_reload():
    from downloader import download
    worker = Process(target=download, args=(start_id, end_id))
    worker.start()


TODO = {
    ACTION.ANSWER:  do_answer,
    ACTION.RELOAD:  do_reload,
}


scheduler = sched.scheduler(time.time, time.sleep)
for i, action in enumerate(ACTION.RANGE):
    TODO[action](action)
scheduler.run()
