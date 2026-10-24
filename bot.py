import html
import os
import asyncio
import json
import subprocess
from queue import Queue, Empty
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from time import sleep
from threading import Thread
from typing import Dict

from telegram import Bot
from telegram.constants import ParseMode


TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])
queue = Queue()


def _log(text) -> None:
    '''
    Print message log with date time
    '''
    print(f'[ {datetime.now().isoformat()} ] -> {text}')


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
        _log('Cannot get machine node name!')
        return 'Unknow'

    node = response.stdout
    return node.strip()


async def _send_telegram_message(node: str, data: Dict) -> None:
    '''
    Send message for telegram CHAT.
    '''
    # Fix logout date if exists.
    try:
        dt = datetime.fromisoformat(data['logout'])
        dt = dt.astimezone(timezone(timedelta(hours=-3)))
        out = dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        out = 'Permanece logado'

    # Create HTML message to send.
    message = (
        f"<b>Atualização de login na máquina {node}</b>\n"
        f"<code>Usuário</code>: {html.escape(str(data['user']))}\n"
        f"<code>TTY</code>: {html.escape(str(data['tty']))}\n"
        f"<code>IP</code>: {html.escape(str(data['hostname']))}\n"
        f"<code>Serviço</code>: {html.escape(str(data['service']))}\n"
        f"<code>Entrada</code>: {html.escape(str(data['login']))}\n"
        f"<code>Saída</code>: {html.escape(str(out))}"
    )

    # Send messagem with BOT.
    async with Bot(TOKEN) as bot:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML,
        )


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
            _log(response.stderr)
            sleep(60.0)
            continue

        _log('Command [ /usr/bin/last ] run successfully!')
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
            _log('Queue is empty!')
            sleep(5.0)
            continue

        # Create a hash from content.
        new = sha256(content).hexdigest()

        # Same hash means "No new login MTF".
        if new == old:
            _log('Not new loggin on server!')
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
   

        # Ordenate by last login date.
        ordened = sorted(data, key=lambda x: x['login'], reverse=True)
        _log(f'New login in {_get_node_name()}\n{ordened[0]}')
        # Send to Telegram.
        asyncio.run(_send_telegram_message(_get_node_name(), ordened[0]))


if __name__ == '__main__':
    _log(f'Running in {_get_node_name()}')
    threads = [
        Thread(target=get_data),
        Thread(target=analyse_data)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

