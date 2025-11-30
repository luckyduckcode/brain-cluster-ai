"""
Async Utils: Helper functions for asynchronous operations.
"""

import asyncio
import functools
from typing import Any, Callable, Coroutine

def async_wrap(func: Callable[..., Any]) -> Callable[..., Coroutine[Any, Any, Any]]:
    """
    Wrap a synchronous function to make it run in an executor.
    Useful for wrapping blocking I/O calls like requests.post.
    """
    @functools.wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_running_loop()
        pfunc = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(None, pfunc)
    return run
