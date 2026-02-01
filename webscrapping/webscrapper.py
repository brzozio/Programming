from lib.wrappers import debugIO, func_timing
import webscrapping.te_scrapper as TEScrapper

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup

import json
from typing import List, Dict, Tuple, Optional

@debugIO
@func_timing
def mat_list_preparing() -> None:
    # Przygotowanie listy materiałów
    products = TEScrapper.scrape_te_products(
        max_pages=75
    )
    print(f"\nŁącznie znaleziono {len(products)} produktów")

    TEScrapper.save_to_json(
        products=products,
        filename="./webscrapping/te_part_numbers.json"
    )


@func_timing
async def fetch_all_requests(part_numbers: list) -> dict: 
    """
    Asynchroniczne pobieranie używając requests w wątkach
    """
    
    def fetch_one_sync(part_number: str) -> Tuple[str, Optional[str]]:
        
        url: str = f"https://www.te.com/en/product-{part_number}.html"
        
        try:  
            resp = requests.get(
                url=url, 
                timeout=20, 
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
            )
            resp.raise_for_status() 

            soup = BeautifulSoup(resp.text, "html.parser")

            div = soup.find("div", class_="documents-list")
            if not div:
                return part_number, None

            for a in div.find_all("a"):
                if a.text and "DS" in a.text:
                    href = a.get("href")
                   
                    if href and href.startswith('/'):
                        href = 'https://www.te.com' + href
                    return part_number, href

            return part_number, None
        
        except requests.exceptions.RequestException as e:
            print(f"Błąd dla {part_number}: {e}")
            return part_number, None
        except Exception as e:
            print(f"Nieoczekiwany błąd dla {part_number}: {e}")
            return part_number, None

    tasks = [asyncio.to_thread(fetch_one_sync, pn) for pn in part_numbers]
    results = await asyncio.gather(*tasks)
    return dict(results)


@func_timing
async def fetch_all_aiohttp(part_numbers: list, max_concurrent: int = 10) -> dict:
    """
    Asynchroniczne pobieranie używając aiohttp z limitem równoczesnych połączeń
    """
    
    async def fetch_one_async(  
        session: aiohttp.ClientSession, 
        part_number: str
    ) -> Tuple[str, Optional[str]]:  
        """Asynchroniczna funkcja pobierająca datasheet dla jednego produktu"""
        
        url: str = f"https://www.te.com/en/product-{part_number}.html"

        try: 
            async with session.get(
                url, 
                timeout=aiohttp.ClientTimeout(total=20) 
            ) as resp:
                resp.raise_for_status() 
                html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")

            div = soup.find("div", class_="documents-list")
            if not div:
                return part_number, None

            for a in div.find_all("a"):
                if a.text and "DS" in a.text:
                    href = a.get("href")
                    
                    if href and href.startswith('/'):
                        href = 'https://www.te.com' + href
                    return part_number, href

            return part_number, None
        
        except aiohttp.ClientError as e: 
            print(f"Błąd dla {part_number}: {e}")
            return part_number, None
        except asyncio.TimeoutError:
            print(f"Timeout dla {part_number}")
            return part_number, None
        except Exception as e:
            print(f"Nieoczekiwany błąd dla {part_number}: {e}")
            return part_number, None

    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_fetch(session, pn):
        """Wrapper ograniczający liczbę równoczesnych połączeń"""
        async with semaphore:
            return await fetch_one_async(session, pn)

    async with aiohttp.ClientSession(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    ) as session:
        tasks = [bounded_fetch(session, pn) for pn in part_numbers]
        results = await asyncio.gather(*tasks)

    return dict(results)


def save_results(results: Dict[str, Optional[str]], filename: str = "results.json") -> None:
    """Zapisuje wyniki do pliku JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nZapisano wyniki do {filename}")


async def main():
    """Główna funkcja"""
    
    try:
        with open('./webscrapping/te_part_numbers.json', 'r') as file:
            part_numbers_list: list = json.load(file)
    except FileNotFoundError:
        print("Plik ./webscrapping/te_part_numbers.json nie istnieje")
        print("Używam przykładowych numerów produktów...\n")
        part_numbers_list = [
            "1-2834018-1",
            "282834-1",
            "282837-1",
            "282834-2",
            "282834-3"
        ]
    
    test_list = part_numbers_list[:10]
    print(f"Testowanie z {len(test_list)} produktami\n")
    
    # results = await fetch_all_aiohttp(test_list, max_concurrent=5)
    results = await fetch_all_requests(test_list)
    
    save_results(results, "datasheets_results.json")


if __name__ == '__main__':
    asyncio.run(main())