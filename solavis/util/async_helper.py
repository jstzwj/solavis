import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_in_executor(method):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, method)
    return result