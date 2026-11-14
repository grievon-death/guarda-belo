import asyncio

import services


def run() -> None:
    tasks = asyncio.gather(
        services.watch_login(),
    )

    asyncio.run(tasks)
