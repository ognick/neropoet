import os
import sys
import zlib
import cPickle
import logging
import progressbar
from settings import settings


_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/datasets/'
logging.basicConfig(
    format='%(asctime)s : %(module)s %(levelname)s : %(message)s',
    level=getattr(logging, settings.get(
        'logging_level', logging.INFO).upper(), logging.INFO)
)


def save(data, file_name):
    if 'datasets' not in file_name:
        file_name = _FOLDER + file_name
    with open(file_name + '.tmp', 'wb') as f:
        f.write(zlib.compress(cPickle.dumps(data, -1)))
    os.rename(file_name + '.tmp', file_name)


def load(file_name):
    if 'datasets' not in file_name:
        file_name = _FOLDER + file_name
    return cPickle.loads(zlib.decompress(open(file_name, 'rb').read()))


def is_exists(file_name):
    if 'datasets' not in file_name:
        file_name = _FOLDER + file_name
    return os.path.exists(file_name)


def add_postfix(name, postfix):
    name, ext = tuple(name.split('.'))
    return ''.join([name, '_', postfix, '.', ext])


def has_postfix(name, postfix):
    name, ext = tuple(name.split('.'))
    return name.split('_')[-1] == postfix


def change_postfix(name, postfix):
    name, ext = tuple(name.split('.'))
    tail = name.split('_')[:-1] + [postfix]
    name = '_'.join(tail)
    return ''.join([name, '.', ext])


def get_bar(*args, **kwargs):
    return progressbar.ProgressBar(*args, **kwargs)
