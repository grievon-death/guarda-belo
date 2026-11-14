import asyncio
import logging
import subprocess


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
        logging.error(response.stderr)
        return 'Unknow'

    node = response.stdout
    return node.strip()
