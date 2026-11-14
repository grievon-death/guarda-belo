import asyncio
import json
import logging
import subprocess
from queue import Queue, Empty
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from time import sleep
from threading import Thread

import services


queue = Queue()


def _get_node_name() -> str:
    '''
    Get machine name
    '''
    response = subprocess.run(
        ['uname', '-n'],
        capture_output=True,
        text=True,
    )

    if response.returncode != 0:
        logging.error(response.stderr)
        return 'Unknow'

    node = response.stdout
    return node.strip()



def get_data() -> None:
    '''
    Send to queue login information
    '''
    while True:
        response = subprocess.run(
            ['/usr/bin/last', '-i', '-j', '-S', '-x', '-n', '5', '--time-format', 'iso'],
            capture_output=True,
            text=True,
        )

        if response.returncode != 0:
            logging.error(response.stderr)
            sleep(60.0)
            continue

        logging.info('Command [ /usr/bin/last ] run successfully!')
        # Convert data to bytes
        data = response.stdout.encode()
        # Send data to process queue.
        queue.put_nowait(data)
        # Wait a minute before try again.
        sleep(60.0)


def analyse_data() -> None:
    """
    Get and process login information from queue
    """
    # Define initial hash.
    old = sha256(b'empty').hexdigest()

    while True:
        try:
            # Get content to be analysed.
            content = queue.get_nowait()
        except Empty:
            logging.debug('Queue is empty!')
            sleep(5.0)
            continue

        # Create a hash from content.
        new = sha256(content).hexdigest()

        # Same hash means "No new login MTF".
        if new == old:
            logging.info('Not new loggin on server!')
            sleep(5.0)
            continue

        # Save new hash for future comparison.
        old = new
        # Decode byte contet to json.
        content = json.loads(content.decode())
        # Get only entries.
        data = content['entries']

        # Fix some information.
        for idx, item in enumerate(data):
            data[idx]['service'] = item['service'].strip()
            dt = datetime.fromisoformat(item['login'])
            dt = dt.astimezone(tz=timezone(timedelta(hours=-3)))
            data[idx]['login'] = dt.strftime('%d/%m/%Y %H:%M:%S')

        logging.warning(f'New login in {_get_node_name()}\n{data}')
        # Send to Telegram.
        asyncio.run(services.send_telegram_message(_get_node_name(), data))


if __name__ == '__main__':
    print(f'Running in {_get_node_name()}')
    threads = [
        Thread(target=get_data),
        Thread(target=analyse_data)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

