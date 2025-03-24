from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import xml.etree.ElementTree as ET
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SEC13F:
    __headers__ = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36"
    }

<<<<<<< Updated upstream
companies = ['BHLB','Apple Inc.','UBS','META','COST',"AMERICAN EXPRESS CO","ABBOTT LABORATORIES "]
for company in companies:
    print(c.cik_lookup(company))

=======
    def __init__(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)

    def get_driver(self):
        """Sets up Selenium WebDriver with proper headers"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set a proper User-Agent to mimic a real browser
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver

    def get_driver(self):
        """Sets up Selenium WebDriver with proper headers"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set a proper User-Agent to mimic a real browser
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver

    def find_stock_holdings(self, cik_key):
        """Finds and extracts `infotable.xml` from the SEC filing page using Selenium"""
        driver = self.get_driver()
        sec_url = f"https://www.sec.gov/edgar/browse/?cik={cik_key}"
        driver.get(sec_url)
        time.sleep(5)  # Allow initial page load

        # ✅ Scroll multiple times to trigger SEC JavaScript loading
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # ✅ Wait for filings list to load dynamically
        try:
            filings_list = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tr"))
            )
        except:
            raise Exception("❌ SEC Filings Table Not Found!")

        # ✅ Extract all rows from the filings table
        soup = BeautifulSoup(driver.page_source, "html.parser")
        filing_rows = soup.find_all("tr")

        # 🛑 Debug: Print extracted rows
        print("\n--- Debug: Extracted Filing Rows ---")
        for row in filing_rows:
            print(row.text.strip())

        # ✅ Find the most recent 13F-HR filing
        latest_filing_url = None
        for row in filing_rows:
            if "13F-HR" in row.text:
                link = row.find("a", href=True)
                if link:
                    latest_filing_url = f"https://www.sec.gov{link['href']}"
                    break  # Stop at the first (latest) match

        if not latest_filing_url:
            raise Exception("❌ No 13F-HR filings found for this company!")

        print(f"📄 Opening latest 13F-HR filing: {latest_filing_url}")

        # 🟢 Open the 13F-HR filing page
        driver.get(latest_filing_url)
        time.sleep(5)

        # ✅ Scroll to ensure all content is loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # ✅ Parse the 13F-HR filing page to find `infotable.xml`
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        # ✅ Find `infotable.xml` instead of `primary_doc.xml`
        xml_links = [a["href"] for a in soup.find_all("a", href=True) if "infotable.xml" in a["href"]]

        if not xml_links:
            raise Exception("❌ No infotable.xml found inside the 13F-HR filing!")

        xml_url = f"https://www.sec.gov{xml_links[0]}"
        print(f"✅ Found XML URL: {xml_url}")

        return self.aggregation_from_sec_xml(xml_url)

    def xml_to_pandas(self, xml_url):
        """Fetches XML from SEC, parses <infoTable> entries, and returns a DataFrame."""
        print(f"📥 Fetching XML data from: {xml_url}")
        time.sleep(2)  # Prevents rate limiting

        response = requests.get(xml_url, headers=self.__headers__)
        if response.status_code != 200:
            raise Exception(f"❌ Failed to fetch XML: {response.status_code}")

        soup = BeautifulSoup(response.text, 'xml')
        info_tables = soup.find_all('infoTable')

        if not info_tables:
            print("⚠️ No <infoTable> found in XML! Check SEC file structure.")
            return pd.DataFrame()

        data = []
        for info in info_tables:
            company_name = info.find('nameOfIssuer')
            total_value = info.find('value')
            shares_table = info.find('shrsOrPrnAmt')

            if company_name and total_value and shares_table:
                shares_owned = shares_table.find('sshPrnamt')
                data.append({
                    "Company Name": company_name.text.strip() if company_name else 'Unknown',
                    "Total Value": int(total_value.text.strip()) if total_value else 0,
                    "Shares Owned": int(shares_owned.text.strip()) if shares_owned else 0
                })

        df = pd.DataFrame(data)
        print(f"✅ Successfully extracted {len(df)} holdings from XML.")
        return df

    def aggregation_from_sec_xml(self, xml_url):
        """Aggregates stock holdings from the SEC XML file."""
        df = self.xml_to_pandas(xml_url)

        if df.empty:
            print("⚠️ No data extracted! Check the XML structure.")
            return

        df_grouped = df.groupby("Company Name", as_index=False).agg({
            'Total Value': 'sum',
            'Shares Owned': 'sum'
        })

        df_grouped = df_grouped.sort_values(by='Total Value', ascending=False).head(5)
        print("\n--- Top 5 Holdings ---")
        print(df_grouped)


# SEC 13F Filing URL - Replace this with the latest filing URL
sec_13f_url = "https://www.sec.gov/Archives/edgar/data/0001067983/000095012325002701/xslForm13F_X02/infotable.xml"


# Function to parse XML and extract stock holdings
def extract_top_holdings(xml_url):
    response = requests.get(xml_url, headers={'User-Agent': 'Mozilla/5.0'})

    if response.status_code != 200:
        raise Exception("❌ Failed to fetch XML data from SEC!")

    # Parse XML
    root = ET.fromstring(response.content)
    holdings = []

    # Extract relevant data
    for info in root.findall('.//infoTable'):
        name = info.find('nameOfIssuer').text
        cusip = info.find('cusip').text
        value = int(info.find('value').text)  # Market value in thousands
        shares = int(info.find('shrsOrPrnAmt/shares').text)

        holdings.append({"Company": name, "CUSIP": cusip, "Market Value ($1000s)": value, "Shares Held": shares})

    # Convert to DataFrame and sort
    df = pd.DataFrame(holdings)
    df = df.sort_values(by="Market Value ($1000s)", ascending=False)

    return df.head(5)  # Return top 5 holdings


# Run function and display results
top_holdings = extract_top_holdings(sec_13f_url)

import ace_tools as tools

tools.display_dataframe_to_user(name="Top 5 Holdings", dataframe=top_holdings)

# --- Run Script ---
if __name__ == "__main__":
    c = SEC13F()
    cik_key = "1067983"  # Replace with the CIK number of the company
    c.find_stock_holdings(cik_key)
>>>>>>> Stashed changes
