import os
import logging

try:
    TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])
    WTMP_PATH = os.environ.get('WTMP_PATH', '/var/log/wtmp')
    ALLOWED_PORTS = os.environ.get('HOST_ALLOWED_PORTS', '22').split(',')
except Exception as e:
    import sys
    logging.error(f'Invalid envfile!')
    sys.exit(1)
