from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import json

def setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def scrape_te_products(max_pages: int | None = 10) -> None:
    
    driver = setup_driver()
    products: list = []
    
    try:
        
        for page_num in range(1, max_pages + 1):

            url = f"https://www.te.com/en/plp/sensors/Y308D.html?n=42710&type=products&p={page_num}&inStoreWithoutPL=false&q2="
            
            wait = WebDriverWait(driver, 15)    
            driver.get(url)
    
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.mat-row")))
                time.sleep(2)
                
                rows = driver.find_elements(By.CSS_SELECTOR, "tr.mat-row")

                for row in rows:

                    divs = row.find_elements(By.CLASS_NAME, "documents-product-drawing")

                    for div in divs:
                        # links = div.find_elements(By.TAG_NAME, "a")
                        # links = div.find_elements(By.CLASS_NAME, "oplp-url-right-grid")
                        # for a in links:

                        #     if a.text not in ('Not EU ELV Compliant', 'EU RoHS Compliant', 'Out of Scope for EU ELV', 'EU RoHS Compliant with Exemptions', 'EU ELV Compliant with Exemptions','Not Yet Reviewed for EU RoHS','Not Yet Reviewed for EU ELV'):
                        #         products.append(a.text)

                        spans = div.find_elements(By.CLASS_NAME, "internal-number")
                        for span in spans:
                            if span.text not in ('TE Internal Number:'):
                                products.append(span.text)

                    
            except TimeoutException:
                print("Timeout - nie udało się załadować produktów")
                break
            except Exception as e:
                print(f"Błąd: {e}")
                break
    
    finally:
        driver.quit()
    
    return products

def save_to_json(products: list, filename: str):

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"Zapisano {len(products)} produktów do {filename}")

if __name__ == "__main__":
    
    products = scrape_te_products(
        max_pages=75
    )
    
    print(f"\nŁącznie znaleziono {len(products)} produktów")

    save_to_json(
        products=products,
        filename="./webscrapping/te_part_numbers.json"
    )