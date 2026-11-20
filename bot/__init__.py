import asyncio

import services


async def run() -> None:
    await asyncio.gather(
        services.watch_login(),
    )
