import asyncio
import aiohttp
import requests
from typing import List
from lib.wrappers import func_timing

URL_TESTING: str = "https://httpbin.org/"

@func_timing
async def test_requests_in_threads(count: int = 100) -> List[int]:

    def fetch_sync() -> int:
        """
            Synchroniczne pobranie, zwraca status code
        """
        try:
            resp = requests.get(URL_TESTING, timeout=10)
            return resp.status_code
        except Exception as e:
            print(f"Błąd requests: {e}")
            return 0
    
    """
        Requests w wątkach używając asyncio.to_thread
    """
    
    tasks = [asyncio.to_thread(fetch_sync) for _ in range(count)]
    results = await asyncio.gather(*tasks)
    
    success = sum(1 for r in results if r == 200)
    print(f"Sukces: {success}/{count}")
    
    return results

@func_timing
async def test_aiohttp(count: int = 100) -> List[int]:

    async def fetch_async(session: aiohttp.ClientSession) -> int:
        try:
            async with session.get(URL_TESTING) as resp:
                return resp.status
        except Exception as e:
            print(f"Błąd aiohttp: {repr(e)}")
            return 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    timeout = aiohttp.ClientTimeout(
        total=60,
        connect=10,
        sock_read=10,
    )

    connector = aiohttp.TCPConnector(
        limit=0, 
        limit_per_host=0
    )

    async with aiohttp.ClientSession(
        headers=headers,
        timeout=timeout,
        connector=connector,
    ) as session:
        tasks = [fetch_async(session) for _ in range(count)]
        results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r == 200)
    print(f"Sukces: {success}/{count}")

    return results

@func_timing
async def test_aiohttp_limited(count: int = 100, max_concurrent: int = 100) -> List[int]:

    async def fetch_async(session: aiohttp.ClientSession) -> int:
        try:
            async with session.get(URL_TESTING) as resp:
                return resp.status
        except Exception as e:
            print(f"Błąd aiohttp: {repr(e)}")
            return 0

    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_fetch(session):
        async with semaphore:
            return await fetch_async(session)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    timeout = aiohttp.ClientTimeout(
        total=60,
        connect=10,
        sock_read=10,
    )

    connector = aiohttp.TCPConnector(
        limit=0,
        limit_per_host=0
    )

    async with aiohttp.ClientSession(
        headers=headers,
        timeout=timeout,
        connector=connector,
    ) as session:
        tasks = [bounded_fetch(session) for _ in range(count)]
        results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r == 200)
    print(f"Sukces: {success}/{count}")

    return results

async def main() -> None:
    
    COUNT = 1_000
    MAX_CONCURRENT = 50
    
    print("="*80)
    print(f"BENCHMARK: {COUNT} zapytań do {URL_TESTING}")
    print(f"Max concurrent: {MAX_CONCURRENT}")
    print("="*80)
    
    output_requests: dict = await test_requests_in_threads(COUNT)
    
    await asyncio.sleep(2)
    
    output_aiohttp_no_limit: dict = await test_aiohttp(COUNT)
    
    await asyncio.sleep(2)
    
    output_aiohttp_limit: dict = await test_aiohttp_limited(COUNT, MAX_CONCURRENT)
    
    # Podsumowanie
    print("\n" + "="*80)
    print("PODSUMOWANIE")
    print("="*80)
    print(f"Test 1 (requests w wątkach):    {sum(1 for r in output_requests['result'] if r == 200)}/{COUNT} sukces.  [{output_requests['time_sec']}s]")
    print(f"Test 2 (aiohttp bez limitu):    {sum(1 for r in output_aiohttp_no_limit['result'] if r == 200)}/{COUNT} sukces.  [{output_aiohttp_no_limit['time_sec']}s]")
    print(f"Test 3 (aiohttp z semaphore):   {sum(1 for r in output_aiohttp_limit['result'] if r == 200)}/{COUNT} sukces.  [{output_aiohttp_limit['time_sec']}s]")


if __name__ == "__main__":
    asyncio.run(main())