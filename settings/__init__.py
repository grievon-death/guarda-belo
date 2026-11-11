import os
import logging

try:
    TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
    CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])
    ALLOWED_PORTS = os.environ['HOST_ALLOWED_PORTS'].strip(',')
except Exception as e:
    import sys
    logging.error(f'Invalid envfile!')
    sys.exit(1)
