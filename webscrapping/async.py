import asyncio
import aiohttp
import requests
from typing import List, Callable
from lib.wrappers import func_timing, debugIO

import json
from bs4 import BeautifulSoup
from pathlib import Path


class TestAsyncURL:
    """
       Klasa do testowania async przy wykrozystaniu requests oraz aiohttp. 
    """

    def __init__(self, concurrency: int = 20, url_testing: str = "https://httpbin.org/", test_count: int = 1_000):
        self.url_testing: str = url_testing
        self.test_count: int = test_count
        self.concurrency: int = concurrency

    @func_timing
    async def test_requests_in_threads(self) -> List[int]:

        def fetch_sync() -> int:
            """
                Synchroniczne pobranie, zwraca status code
            """
            try:
                resp = requests.get(self.url_testing, timeout=10)
                return resp.status_code
            except Exception as e:
                print(f"Błąd requests: {e}")
                return 0
        
        """
            Requests w wątkach używając asyncio.to_thread
        """
        
        tasks = [asyncio.to_thread(fetch_sync) for _ in range(self.test_count)]
        results = await asyncio.gather(*tasks)
        
        success = sum(1 for r in results if r == 200)
        print(f"Sukces: {success}/{self.test_count}")
        
        return results

    @func_timing
    async def test_aiohttp(self) -> List[int]:

        async def fetch_async(session: aiohttp.ClientSession) -> int:
            try:
                async with session.get(self.url_testing) as resp:
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
            tasks = [fetch_async(session) for _ in range(self.test_count)]
            results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r == 200)
        print(f"Sukces: {success}/{self.test_count}")

        return results

    @func_timing
    async def test_aiohttp_limited(self) -> List[int]:

        async def fetch_async(session: aiohttp.ClientSession) -> int:
            try:
                async with session.get(self.url_testing) as resp:
                    return resp.status
            except Exception as e:
                print(f"Błąd aiohttp: {repr(e)}")
                return 0

        semaphore = asyncio.Semaphore(self.concurrency)

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
            tasks = [bounded_fetch(session) for _ in range(self.test_count)]
            results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r == 200)
        print(f"Sukces: {success}/{self.test_count}")

        return results

class AsyncURL:
    """
        Klasa do uruchamiania web async.
    """

    def __init__(self, concurrency: int = 20):
        self.concurrency: int = concurrency

    @func_timing
    async def run(self, url_list: list = None, resp_mod: Callable = None) -> dict:
        """
            Docstring for run
            
            :param url_list: Lista URL
                :type url_list: list

            :param resp_mod: Function injection - jesli chcemy wykonac jakas operacje na reponse.
                :type resp_mod: Callable 

            :return: Description
                :rtype: dict
        """

        async def fetch_async(session: aiohttp.ClientSession, url: str, fetch_resp_mod: Callable = None) -> dict:
            try:
                async with session.get(url=url) as resp:
                    html: str = await resp.text()

                if fetch_resp_mod is not None:
                    await asyncio.to_thread(fetch_resp_mod, html=html, url=url)

                return {
                    'status': resp.status
                }
            except Exception as e:
                print(f"Błąd aiohttp: {repr(e)}")
                return 0

        async def bounded_fetch(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession, bounded_url: str, bounded_resp_mod: Callable = None):
            async with semaphore:
                return await fetch_async(
                    session=session,
                    url=bounded_url,
                    fetch_resp_mod=bounded_resp_mod
                )
        sem = asyncio.Semaphore(self.concurrency)
        
        headers: dict = {
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
            tasks = [
                bounded_fetch(
                    semaphore=sem,
                    session=session,
                    bounded_url=url,
                    bounded_resp_mod=resp_mod
                ) 
                for url in url_list
            ]
            results = await asyncio.gather(*tasks)

        return {
            'success': float(sum(1 for el in results if el['status'] == 200)/len(url_list)),
            # 'working_urls_data': [el['text'] for el in results if el['status'] == 200]
        }


async def main() -> None:

    def find_swagger_div_and_save(output_file: str = "swagger_results.json", **kwargs) -> None:
        """
            Szuka wszystkich <div> i sprawdza, czy któryś ma klasę 'swagger'.
            Jeśli tak, dopisuje wynik do pliku JSON w formacie:
            {"url": ..., "found": True}

            :param html: Treść strony
            :param url: URL strony (do zapisania)
            :param output_file: Plik JSON do dopisania
        """
        if 'html' in kwargs and 'url' in kwargs:
            soup = BeautifulSoup(kwargs['html'], "html.parser")
            divs = soup.find_all("div", class_="swagger-ui")

            if divs:
                data = {"url": kwargs['url'], "found": True}
                path = Path(output_file)

                if path.exists():
                    try:
                        with path.open("r", encoding="utf-8") as f:
                            existing = json.load(f)
                    except json.JSONDecodeError:
                        existing = []
                else:
                    existing = []

                existing.append(data)

                with path.open("w", encoding="utf-8") as f:
                    json.dump(existing, f, ensure_ascii=False, indent=2)

    
    COUNT, CONCURRENCY = 100, 20

    def printing(input: str) -> None:
        print(input)

    async_instacne: AsyncURL = AsyncURL()

    output = await async_instacne.run(
        url_list=['https://httpbin.org/' for _ in range(100)],
        resp_mod=find_swagger_div_and_save
    )

    # async_instance: TestAsyncURL = TestAsyncURL(
    #     concurrency=CONCURRENCY,
    #     url_testing="https://httpbin.org/",
    #     test_count=COUNT
    # )
    
    # output_requests: dict = await async_instance.test_requests_in_threads()
    
    # await asyncio.sleep(2)
    
    # output_aiohttp_no_limit: dict = await async_instance.test_aiohttp()
    
    # await asyncio.sleep(2)
    
    # output_aiohttp_limit: dict = await async_instance.test_aiohttp_limited()
    
    # # Podsumowanie
    # print("\n" + "="*80)
    # print("PODSUMOWANIE")
    # print("="*80)
    # print(f"Test 1 (requests w wątkach):    {sum(1 for r in output_requests['result'] if r == 200)}/{COUNT} sukces.  [{output_requests['time_sec']}s]")
    # print(f"Test 2 (aiohttp bez limitu):    {sum(1 for r in output_aiohttp_no_limit['result'] if r == 200)}/{COUNT} sukces.  [{output_aiohttp_no_limit['time_sec']}s]")
    # print(f"Test 3 (aiohttp z semaphore):   {sum(1 for r in output_aiohttp_limit['result'] if r == 200)}/{COUNT} sukces.  [{output_aiohttp_limit['time_sec']}s]")


if __name__ == "__main__":
    asyncio.run(main())