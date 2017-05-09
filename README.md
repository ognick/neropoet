# Neropoet


Lyrics generator for <b>russian language</b> based on users posts in the <a href="https://vk.com">vk.com</a> .



## Install:

#### 1. Execute: ``` pip install -r requirements.txt ```
#### 2. Make ./credentials.py:
<a href="https://vk.com/dev/authentication">read more</a>
```
 credentials = {
    'group_token': 'group_token',
    'app_token': app_token',
    'bot_auth': {
        'app_id': '3031599',
        'user_login': 'your_login',
        'user_password': 'your_pass',
    },
    'group_id': 'neropoet',
    'blacklist': [349746767],
    'tester_ids': [4294291],
}
```

#### 3. Download word2vec model <a href="https://vk.com/doc4294291_445594054">wiki-model.bin</a> and move to ```./dictionary/wiki-model.bin```


## Run:
### Console:
##### 1. ``` ./downloader.py [start_id] [end_id] ```
##### 2. ``` ./poet.py datasets/vk_[start_id]_[end_id]_ext.bin ```
### GUI:
##### 1. ``` ./autorun.py [start_id] [end_id] ```

