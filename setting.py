import os
env_path = './.env'

with open(env_path, 'r') as f:
    for line in f.readlines():
        # 跳出空白行
        if not line.strip():
            continue

        line = line.replace('\n', '')
        if not line.startswith('#'):
            key = line.split('=', 1)[0]
            val = line.split('=', 1)[1]
            os.environ[key] = val