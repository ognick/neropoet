settings = {
    'group_id': 'neropoet',
    'max_post_count': 100,
    'max_block_count': 10,
    'sleep': 0.30,
    'similarity_threshold': 0.3,
    'logging_level': 'INFO',
    'spam_mode': False,
    'auto_reply_delay': 172800,
    'processes': 1,
    'is_tmp_file': False,

    'answer': 1,
    'reload': 1200,

    'blacklist': [349746767],
    'tester_ids': [4294291],

    'style': 'random',
}

try:
    from credentials import credentials
    settings.update(credentials)
except ImportError:
    try:
        import os
        env = os.environ
        settings.update({
            'group_token': env['group_token'],
            'app_token': env['app_token'],
            'bot_auth' : {
                'app_id': env['app_id'],
                'user_login': env['user_login'],
                'user_password': env['user_password'],
            },
        })
        for name in ['processes', 'answer', 'reload']:
            if name in env:
                settings[name] = int(env[name])
    except:
        raise

