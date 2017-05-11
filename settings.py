from credentials import credentials
settings = {
    'max_post_count': 100,
    'max_block_count': 10,
    'sleep': 0.30,
    'similarity_threshold': 0.3,
    'logging_level': 'INFO',
    'auto_reply_delay': 172800,
    'processes': 4
}
settings.update(credentials)
