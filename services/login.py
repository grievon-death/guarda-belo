import asyncio
import json
import logging
from asyncio.queues import Queue, QueueEmpty, QueueFull
from hashlib import sha256
from typing import List

import services
import models

from .messager import send_telegram_message
from .tux import get_node_name


_LOGIN_QUEUE = Queue(maxsize=10)


async def _queue_login_data() -> None:
    '''
    Send to queue login information
    '''
    while True:
        data: List[models.UTMPDecodedData] = await services.get_last_content()

        try:
            # Send data to process queue.
            _LOGIN_QUEUE.put_nowait(data[0])
        except QueueFull:
            logging.warning('Queue full. Wait a second!')
        except Exception as e:
            import sys
            logging.error(e)
            sys.exit(1)

        del data
        # Wait a minute before try again.
        await asyncio.sleep(1)


async def _login_analises() -> None:
    """
    Get and process login information from queue
    """
    # Define initial hash.
    old = sha256(b'empty').hexdigest()
    node = await get_node_name()

    while True:
        last_login = models.LastLogin()

        try:
            # Get content to be analysed.
            data: models.UTMPDecodedData = _LOGIN_QUEUE.get_nowait()
        except QueueEmpty:
            logging.debug('Queue is empty!')
            del last_login
            await asyncio.sleep(0.5)
            continue

        _to_check_sum = json.dumps(data.__dict__, sort_keys=True).encode()
        # Create a hash from content.
        new = sha256(_to_check_sum).hexdigest()

        # Same hash means "No new login MTF".
        if new == old:
            logging.info('Not new loggin on server!')
            del last_login
            await asyncio.sleep(0.5)
            continue

        # Save new hash for future comparison.
        old = new
        logging.warning(f'New login in {node}\n{data}')
        # Send to Telegram.
        await send_telegram_message(node, last_login)
        del last_login


async def watch_login() -> None:
    """
    Inicia processos que analisam entradas e saídas da máquina.
    """
    await asyncio.gather(
        _queue_login_data(),
        _login_analises(),
    )
