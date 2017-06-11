settings = {
    'group_id': 'neropoet',
    'max_post_count': 500,
    'max_block_count': 10,
    'sleep': 0.30,
    'similarity_threshold': 0.3,
    'logging_level': 'DEBUG',
    'spam_mode': True,
    'auto_reply_delay': 172800,
    'processes': 1,
    'is_tmp_file': False,

    'answer': 10,
    'reload': 1200,

    'blacklist': [349746767],
    'tester_ids': [4294291],

    'style': 'random',

    'publics': [
        {
            'id': -30022666,
            'name': 'Lepra'
        },
        {
            'id': -35927256,
            'name': 'krutiecitati'
        },
        {
            'id': -27456813,
            'name': 'pachanskie'
        },
        {
            'id': -50198422,
            'name': 'eroticheskie_rasskazy'
        }
    ],

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

