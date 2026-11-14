import asyncio
import json
import logging
import subprocess
from asyncio.queues import Queue, QueueEmpty, QueueFull
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Dict, List

from .messager import send_telegram_message
from .tux import get_node_name


_LOGIN_QUEUE = Queue(maxsize=10)
_ERROR_SLEEP_TIME = 30.0
_OK_SLEEP_TIME = 15.0
_READQ_SLEEP_TIME = 5.0


async def _queue_login_data() -> None:
    '''
    Send to queue login information
    '''
    while True:
        response = await asyncio.to_thread(
            subprocess.run,
            ['/usr/bin/last', '-i', '-j', '-S', '-x', '-n', '1', '--time-format', 'iso'],
            capture_output=True,
            text=True,
        )

        if response.returncode != 0:
            logging.error(response.stderr)
            await asyncio.sleep(_ERROR_SLEEP_TIME)
            continue

        logging.info('Command [ /usr/bin/last ] run successfully!')
        # Convert data to bytes
        data: bytes = response.stdout.encode()

        try:
            # Send data to process queue.
            _LOGIN_QUEUE.put_nowait(data)
        except QueueFull:
            # Wait a minute before try again.
            await asyncio.sleep(_OK_SLEEP_TIME)
            # Send data to process queue.
            _LOGIN_QUEUE.put_nowait(data)
        except Exception as e:
            import sys
            logging.error(e)
            sys.exit(1)

        # Wait a minute before try again.
        await asyncio.sleep(_OK_SLEEP_TIME)


async def _login_analises() -> None:
    """
    Get and process login information from queue
    """
    # Define initial hash.
    old = sha256(b'empty').hexdigest()
    node = await get_node_name()

    while True:
        try:
            # Get content to be analysed.
            content: bytes = _LOGIN_QUEUE.get_nowait()
        except QueueEmpty:
            logging.debug('Queue is empty!')
            await asyncio.sleep(_READQ_SLEEP_TIME)
            continue

        # Create a hash from content.
        new = sha256(content).hexdigest()

        # Same hash means "No new login MTF".
        if new == old:
            logging.info('Not new loggin on server!')
            await asyncio.sleep(_READQ_SLEEP_TIME)
            continue

        # Save new hash for future comparison.
        old = new
        # Decode byte contet to json.
        raw_data: Dict[str, List] = json.loads(content.decode())
        # Get only entries.
        data: Dict = raw_data['entries'][0]
        # Fix some information.
        data['service'] = data['service'].strip()
        dt = datetime.fromisoformat(data['login'])
        dt = dt.astimezone(tz=timezone(timedelta(hours=-3)))
        data['login'] = dt.strftime('%d/%m/%Y %H:%M:%S')

        logging.warning(f'New login in {node}\n{data}')
        # Send to Telegram.
        await send_telegram_message(node, data)


async def watch_login() -> None:
    """
    Inicia processos que analisam entradas e saídas da máquina.
    """
    await asyncio.gather(
        _queue_login_data(),
        _login_analises(),
    )
