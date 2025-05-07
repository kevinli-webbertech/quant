import datetime
import platform
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from functools import lru_cache
import argparse 

class SECForm4Scraper:
    __headers__ = {
        "User-Agent": "test@gmail.com"
    }

    __LINUX_CHROME_DRIVER_PATH__ = '/usr/bin/chromedriver'

    def __init__(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)


    # Check if the system is Linux
    @lru_cache(maxsize=256)
    def __is_linux(self):
        return platform.system() == "Linux"

    def get_driver(self):
         # required to access sec gov pages (via documentation)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('user-data-dir=/tmp/chrome_headless')
        chrome_options.add_argument("start-maximized")
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")

        if self.__is_linux():
            driver = webdriver.Chrome(service=Service(self.__LINUX_CHROME_DRIVER_PATH__), options=chrome_options)
        else:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        return driver

    def get_form4_filings(self, cik, filing_date=None, to_date=None):
        driver = self.get_driver()
        base_url = f"https://www.sec.gov/edgar/browse/?CIK={cik}&owner=only&action=getcompany&type=4"
        driver.get(base_url)

        try:
            view_all_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "btnViewAllFilings"))
            )
            if "hidden" not in view_all_button.get_attribute("class"):
                view_all_button.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "filingsTable"))
                )
        except Exception as e:
            print(f"Could not expand filings: {e}")

        if filing_date:
            try:
                 # Wait for date inputs to exist
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "filingDateFrom")))
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "filingDateTo")))

                from_input = driver.find_element(By.ID, "filingDateFrom")
                to_input = driver.find_element(By.ID, "filingDateTo")

                driver.execute_script("arguments[0].removeAttribute('readonly')", from_input)
                driver.execute_script("arguments[0].removeAttribute('readonly')", to_input)

                driver.execute_script("arguments[0].removeAttribute('disabled')", from_input)
                driver.execute_script("arguments[0].removeAttribute('disabled')", to_input)

                from_input.clear()
                to_input.clear()

                from_input.send_keys(filing_date)
                from_input.send_keys(Keys.RETURN)
                driver.implicitly_wait(5)
                if to_date:
                    to_input.send_keys(to_date)
                    to_input.send_keys(Keys.RETURN)
                WebDriverWait(driver, 15). until(
                    EC.presence_of_element_located((By.ID, "filingsTable"))
                )
            except TimeoutException as e:
                print(f"Timeout exception when filtering by date: {e}")
            except Exception as e:
                print(f"Could not filter by date: {e}")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        data_export_divs = soup.find_all("div", {"data-export": "Statement of changes in beneficial ownership of securities "})

        if not data_export_divs:
            print(f"No 4F filings found for CIK {cik} on date {filing_date}")

        result = []
        limit = len(data_export_divs) if filing_date else 5 # Result limit, default: 5
        print(f"{limit} filings found")
        for div in data_export_divs[:limit]:
            a_tag = div.find("a", class_="filing-link-all-files")
            if not a_tag:
                continue
            selected_filing_url = "https://www.sec.gov" + a_tag.get("href")

            print("Found the .htm link:", selected_filing_url)
            response = requests.get(selected_filing_url, headers=self.__headers__)
            soup = BeautifulSoup(response.text, 'html.parser')

            filing_date_text = soup.find('div', class_='formGrouping').find('div', class_='info').get_text().strip()
            links = soup.find_all('a', href=True)
            infotable_links = [link.get('href') for link in links if link.get('href').endswith('.xml')]
            if not infotable_links:
                raise Exception("No XML files found.")

            xml_url = "https://www.sec.gov" + infotable_links[-1]
            print("latest_4q_filing XML url:", xml_url)

            xml_response = requests.get(xml_url, headers=self.__headers__)
            df = parse_derivative_transactions(xml_response, filing_date_text)  # Optional: Add `filing_date` "2024-11-13"
            if len(df) != 0:
                result.extend(df)
                print(df)
            else:
                print("No filings found.")

        return result

def parse_derivative_transactions(xml, filing_date_text):
    soup = BeautifulSoup(xml.text, "xml")
    transactions = []
    issuer = soup.find("issuer")
    company_cik = safe_get_text(issuer, ["issuerCik"])
    company_name = safe_get_text(issuer, ["issuerName"])

    owner = soup.find("reportingOwner")
    owner_cik = safe_get_text(owner, ["reportingOwnerId", "rptOwnerCik"])
    owner_name = safe_get_text(owner, ["reportingOwnerId", "rptOwnerName"])
    owner_title = safe_get_text(owner, ["reportingOwnerRelationship", "officerTitle"])
    for tx in soup.find_all("derivativeTransaction"):
        title = tx.securityTitle.value.text.strip()
        code = tx.transactionCoding.transactionCode.text.strip()
        action = tx.transactionAcquiredDisposedCode.value.text.strip()

        is_put = "put option" in title.lower()
        is_call = "call option" in title.lower() or "stock option" in title.lower()

        kind = "PUT" if is_put else "CALL" if is_call else "OTHER"

        action_type = {
            "A": "Acquired",
            "D": "Disposed"
        }.get(action, "Unknown")

        # Classify trade category
        if kind == "CALL" and code == "M" and action_type == "Disposed":
            trade_category = "Sell after Exercising Option"
        elif code == "P" and action_type == "Acquired":
            trade_category = "Buy"
        elif code == "S":
            trade_category = "Sell"
        elif code == "A":
            trade_category = "Awarded"
        elif kind == "PUT":
            trade_category = "Put Option"
        else:
            trade_category = "Other"

        transactions.append({
            "Company CIK": company_cik,
            "Company Name": company_name,
            "Owner CIK": owner_cik,
            "Owner Name": owner_name,
            "Owner Title": owner_title,
            "Type": kind,
            "Title": title,
            "Transaction Code": code,
            "Action": action_type,
            "Filing Date": filing_date_text,
            "Trade Category": trade_category
        })
    if len(transactions) == 0:
        transactions.append({
            "Company CIK": company_cik,
            "Company Name": company_name,
            "Owner CIK": owner_cik,
            "Owner Name": owner_name,
            "Owner Title": owner_title
        })
    return transactions

def safe_get_text(soup, tag_chain, default="N/A"):
    try:
        for tag in tag_chain:
            soup = soup.find(tag)
            if soup is None:
                return default
        return soup.get_text(strip=True)
    except Exception:
        return default

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--export_csv", help="Specify the filename to export dataframe to CSV.")
    args = parser.parse_args()
    
    scraper = SECForm4Scraper()

    companies = {
        "Tesla": "0001318605",
        "Meta": "0001326801",
        "Apple": "0000320193",
        "asdf":  "0001067983"
    }
    df = pd.DataFrame()
    result = []
    # Date range
    filing_date="2024-11-01"
    to_date="2025-04-01"
    for name, cik in companies.items():
        print(f"\n📄 Insider Form 4 Filings for {name}")
        result.extend(scraper.get_form4_filings(cik, filing_date, to_date))  # Optional: Add `filing_date` "2024-11-13" and/or `to_date`
    df = pd.json_normalize(result)
    print("\n-------------------------------------------------------------------------------------------Form 4--------------------------------------------------------------------------------------------")
    if filing_date is None:
        print("NO DATE RANGE")
    elif to_date is None:
        print(f"DATE RANGE: {filing_date} to present")
    else:
        print(f"DATE RANGE: {filing_date} to {to_date}")
    print(df)

    if args.export_csv:
        try:
            with open(args.export_csv, "w", encoding="utf-8") as file:
                range=f"{filing_date} to {to_date}"
                file.write(range+"\n")
                df.to_csv(file, index=True)
            print(f"\n💾 DataFrame exported to: {args.export_csv}")
        except Exception as e:
            print(f"\n⚠️ Error exporting to CSV: {e}")

