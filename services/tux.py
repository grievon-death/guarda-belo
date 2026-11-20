import asyncio
import logging
import sys
import subprocess
from datetime import datetime, timezone
from struct import Struct
from typing import List

import models
import settings


_UTMP = Struct('hi32s4s32s256shhiii4i20s')


def _read_wtmp_auth_file() -> List[models.UTMPRawData]:
    response = []

    with open(settings.WTMP_PATH, 'rb') as file:
        while chunk := file.read(_UTMP.size):
            if len(chunk) < _UTMP.size:
                break
            response.append(models.UTMPRawData.from_bytes(chunk, _UTMP))

    return response


async def get_node_name() -> str:
    """
    Captura o nome da máquina em que se está executando o BOT.
    """
    response = await asyncio.to_thread(
        subprocess.run,
        ['uname', '-n'],
        capture_output=True,
        text=True,
    )

    if response.returncode != 0:
        logging.error(f'Cannot get node name.\nCause {response.stderr}')
        sys.exit(1)

    node = response.stdout
    return node.strip()


async def get_last_content(max_response: int=5) -> List[models.UTMPDecodedData]:
    """
    Captura os últimos dados de login na máquina.
    """
    raw_content = await asyncio.to_thread(_read_wtmp_auth_file)
    raw_content = sorted(raw_content, key=lambda x: x.timestamp, reverse=True)[:max_response]
    response = []

    for raw_data in raw_content:
        data = models.UTMPDecodedData()
        remote_hosts = []
        reserved = []

        for host in raw_data.remote_host.split(b'\0'):
            if len(host) > 0: remote_hosts.append(host.decode())
        for r in raw_data.reserved.split(b'\0'):
            if len(r) > 0: reserved.append(r.decode())

        at = datetime.fromtimestamp(raw_data.timestamp)
        data.user_name = raw_data.user_name.split(b'\0')[0].decode()
        data.user_terminal = raw_data.user_terminal.split(b'\0')[0].decode()
        data.remote_addr = '.'.join([str(r) for r in raw_data.remote_addr])
        data.pid = raw_data.pid
        data.process_exit_code = raw_data.process_exit_code
        data.process_finish_code = raw_data.process_finish_code
        data.registry_type = raw_data.registry_type
        data.session_id = raw_data.session_id
        data.timestamp = raw_data.timestamp
        data.timestamp_microsec = raw_data.timestamp_microsec
        data.at = at.replace(tzinfo=timezone.utc)
        response.append(data)

    return response
