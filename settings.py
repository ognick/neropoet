settings = {
    'group_id': 'neropoet',
    'max_post_count': 100,
    'max_block_count': 10,
    'sleep': 0.30,
    'similarity_threshold': 0.3,
    'logging_level': 'INFO',
    'auto_reply_delay': 172800,
    'processes': 4,
    'answer': 10,
    'reload': 1200,

    'blacklist': [349746767],
    'tester_ids': [4294291],
}

try:
    from credentials import credentials
    settings.update(credentials)
except ImportError:
    pass

try:
    import os
    env = os.environ
    settings.update({
        'group_token': env.get('group_token'),
        'bot_auth' : {
            'app_id': env.get('app_id'),
            'user_login': env.get('user_login'),
            'user_password': env.get('user_password'),
        },
    })
except:
    pass

