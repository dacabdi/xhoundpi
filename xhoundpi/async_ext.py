""" byte io extensions """

import asyncio
from typing import Coroutine

async def loop_forever_async(coro: Coroutine, *args, **kwargs):
    """ Runs a couroutine on an infinite loop """
    while True:
        await coro(*args, **kwargs)

def run_sync_with_loop(loop, coro: Coroutine, timeout=1):
    """ Run sync on provided event loop with timeout """
    return loop.run_until_complete(asyncio.wait_for(coro, timeout))

def run_sync(coro: Coroutine, timeout=1):
    """ Run sync on main event loop with timeout """
    loop = asyncio.get_event_loop()
    return run_sync_with_loop(loop, coro, timeout)
