import datetime
import time
import platform
import requests
import pandas as pd
from SEC13F_util import *
from bs4 import BeautifulSoup
from selenium import webdriver
from functools import lru_cache
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SEC13F:
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
        if platform.system() == "Linux":
            return True
        else:
            return False

    """
    param: cik_key (https://www.sec.gov/files/company_tickers.json)
    return: the source code of the url of the following,

    https://www.sec.gov/edgar/browse/?cik=1350694

    For invert and forward search of company name using Edgar Search please refer to the URLs in the README.md in this folder.
    """

    @lru_cache(maxsize=256)
    def __get_page_source(self, cik_key, filing_date=None):
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

        driver.get(f"https://www.sec.gov/edgar/browse/?cik={cik_key}")
        driver.implicitly_wait(10)

        # If a filing date is provided, set the date fields and trigger the search
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
                to_input.send_keys(filing_date)
                to_input.send_keys(Keys.RETURN)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{filing_date}')]"))
                )


            except Exception as e:
                print(f"⚠️ Date filter interaction failed: {e}")

        page_source = driver.page_source
        driver.quit()
        return page_source

    """
    finds first htm link on the sec gov page and then fetches it.
    It should be the latest quant_analysis-HR filing.
    """
    def __find_htm_link(self, soup):
        data_export_div = soup.find("div",
                                    {"data-export": "Quarterly report filed by institutional managers, Holdings "})
        if data_export_div is None:
            raise Exception("Div with the data-export attribute not found.")

        a_tag = data_export_div.find_all("a", class_="filing-link-all-files")
        if a_tag:
            href = a_tag[0].get("href")
            filing_url = "https://sec.gov" + href
            print("Found the .htm link:", filing_url)
            return filing_url
        else:
            print("No .htm link found within the div.")

    """
    param: cik_key
    return: top holdings of the specified company based on the xml from SEC website.
    Example: https://www.sec.gov/Archives/edgar/data/1350694/000117266125000823/infotable.xml
    """
    def find_stock_holdings(self, cik_key, filing_date=None):
        page_source = self.__get_page_source(cik_key, filing_date)
        soup = BeautifulSoup(page_source, "html.parser")

        # Find first quant_analysis-HR result from the filtered page
        data_export_divs = soup.find_all("div", {"data-export": "Quarterly report filed by institutional managers, Holdings "})

        if not data_export_divs:
            raise Exception(f"No quant_analysis-HR filings found for CIK {cik_key} on date {filing_date}")

        for div in data_export_divs:
            a_tag = div.find("a", class_="filing-link-all-files")
            if a_tag:
                selected_filing_url = "https://www.sec.gov" + a_tag.get("href")
                break
        else:
            raise Exception("No .htm link found within filing entry.")

        print("Found the .htm link:", selected_filing_url)
        response = requests.get(selected_filing_url, headers=self.__headers__)
        soup = BeautifulSoup(response.text, 'html.parser')

        filing_date_text = soup.find('div', class_='formGrouping').find('div', class_='info').get_text().strip()
        links = soup.find_all('a', href=True)
        infotable_links = [link.get('href') for link in links if link.get('href').endswith('.xml')]
        if not infotable_links:
            raise Exception("No XML files found.")

        xml_url = "https://www.sec.gov" + infotable_links[-1]
        print("latest_13f_filing XML url:", xml_url)

        xml_response = requests.get(xml_url, headers=self.__headers__)
        soup = BeautifulSoup(xml_response.text, 'xml')
        info_tables = soup.find_all('infoTable')

        data = []
        for info in info_tables:
            company_name = info.find('nameOfIssuer').text if info.find('nameOfIssuer') else 'None'
            total_value = int(info.find('value').text) if info.find('value') else 0
            shares_table = info.find('shrsOrPrnAmt')
            shares_owned = int(shares_table.find('sshPrnamt').text) if shares_table and shares_table.find('sshPrnamt') else 0
            data.append({
                'Company Name': company_name,
                'Total Value': total_value,
                'Shares Owned': shares_owned,
                'Filing Date': filing_date_text
            })

        df = pd.DataFrame(data)
        df = df.groupby('Company Name', as_index=False).agg({
            'Total Value': 'sum',
            'Shares Owned': 'sum',
            'Filing Date': 'first'
        })

        df.sort_values(by='Total Value', ascending=False, inplace=True)
        df['Total Value'] = df['Total Value'].astype(str)
        df['Shares Owned'] = df['Shares Owned'].astype(str)

        for index, row in df.iterrows():
            total_value = int(row['Total Value'])
            shares_owned = int(row['Shares Owned'])
            df.at[index, 'Total Value'] = divisibleBy(total_value)
            df.at[index, 'Shares Owned'] = divisibleBy(shares_owned)

        return df



    """
    TODO:
        Darren please try this, try to cut the code logic from the bulky logic from the original line 121 to 164
    parameter: https://www.sec.gov/Archives/edgar/data/1350694/000117266125000823/infotable.xml
    return: formated output
    """



    def xml_to_pandas(self, xml_url):
        """
        Fetches the XML from SEC, parses the <infoTable> entries,
        and returns a pandas DataFrame.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.sec.gov/",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
        }

        # 🔴 Use a session to make SEC requests look more legitimate
        session = requests.Session()
        session.headers.update(headers)

        # 🔴 SEC blocks rapid requests, so add a delay
        time.sleep(2)  # Wait 2 seconds before making the request

        try:
            response = session.get(xml_url, timeout=10)
            response.raise_for_status()  # Raise error if request fails
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching XML: {e}")
            return pd.DataFrame()  # Return empty DataFrame to prevent crashes

        xml_content = response.text
        print("\n--- Raw XML Content (First 500 Characters) ---")
        print(xml_content[:500])  # Print first 500 characters to check structure

        soup = BeautifulSoup(xml_content, 'xml')

        # 🛑 Debugging: Check if <infoTable> exists
        info_tables = soup.find_all('infoTable')
        print(f"\n--- Found {len(info_tables)} <infoTable> entries ---")

        if not info_tables:
            print("⚠️ No <infoTable> found in XML! XML structure may have changed.")
            return pd.DataFrame()  # Return empty DataFrame to prevent crashes

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

        # 🛑 Debugging: Print DataFrame before returning
        print("\n--- DataFrame Extracted ---")
        print(df.head())
        print("Columns:", df.columns)
        print(f"Total Rows: {len(df)}\n")

        return df

    def aggregation_from_sec_xml(self, xml_url):
        df = self.xml_to_pandas(xml_url)

        # Ensure the DataFrame is not empty and has the expected column
        if df.empty:
            print("Error: DataFrame is empty! Check XML structure.")
            return

        expected_columns = {"Company Name", "Total Value", "Shares Owned"}
        missing_columns = expected_columns - set(df.columns)

        if missing_columns:
            print(f"Error: Missing columns in DataFrame: {missing_columns}")
            return

        # Group by Company Name and aggregate Total Value and Shares Owned
        df_grouped = df.groupby("Company Name", as_index=False).agg({
            'Total Value': 'sum',
            'Shares Owned': 'sum'
        })

        # Sort to get the top 5 holdings based on Total Value
        df_grouped = df_grouped.sort_values(by='Total Value', ascending=False).head(5)

        print("\n--- Top 5 Holdings ---")
        print(df_grouped)

    """"
    just lookup for one company name to cik.
    """
    def cik_lookup(self, company_name):
        # 1350694
        company_tickers = requests.get("https://www.sec.gov/files/company_tickers.json",headers=self.__headers__)

        company_data = pd.DataFrame.from_dict(company_tickers.json(), orient='index')

        #fill all ciks with leading zeros for proper cik key
        company_data['cik_str'] = company_data['cik_str'].astype(str).str.zfill(10)

        #check to see if its one word (ticker) or multiple words (the company title name)
        if len(company_name.split()) == 1:
            company_name = company_name.upper().strip()

            if not company_data[company_data['ticker'] == company_name].empty:
                #grabs first cik_str of row it sees
                cik_str = company_data[company_data['ticker'] == company_name]['cik_str'].iloc[0]
                return cik_str
            else:
                raise Exception(f"Ticker {company_name} not found.")

        ## case sensitivity check, use "Apple Inc" vs "Apple INC"
        else:
            if not company_data[company_data['title'] == company_name.strip()].empty:
                #grabs first cik_str of row it sees
                cik_str = company_data[company_data['title'] == company_name.strip()]['cik_str'].iloc[0]
                return cik_str
            else:
                print(f"Company {company_name} not found.")


    """
    Finds overlapping stocks based on *args number of stock dataframes placed into the parameter
    Make sure you use the find_stock_holdings() function to generate stock holding dataframes and
    input them into this function.

    Example:
        c = SEC13F()
        c.find_common_holdings_multi_cik(tuple(['1350694', '1067983', '1037389', '1610520']))

    Output: A list of company names, displayed vertically.
    """
    def find_common_holdings_multi_cik(self, list_of_ciks, filing_date=None):
        if len(list_of_ciks) == 0:
            raise Exception("Invalid input, please check function definitions.")

        data_frames = []
        for cik in list_of_ciks:
            try:
                data_frames.append(self.find_stock_holdings(cik, filing_date=filing_date))
            except Exception as e:
                print(f"Error for CIK {cik}: {e}")

        if not data_frames:
            print("No valid filings retrieved.")
            return

        same_holdings = aggregate_holdings(data_frames)
        print("\n------------------Shared Stock Holdings---------------------")
        shared_holdings = same_holdings.split(",")
        for holding in shared_holdings:
            print(holding.strip())
        print("\n------------------End Stock Holdings---------------------")



if __name__ == "__main__":
    c = SEC13F()

    companies = ['BHLB', 'Apple Inc.', 'UBS', 'META', 'COST', "AMERICAN EXPRESS CO", "ABBOTT LABORATORIES "]
    ciks = {}

    print("\n------------------Company Names------------------------")
    print("NAME                                             CIK")

    try:
        for company in companies:
            ciks[company] = c.cik_lookup(company)
    except Exception as e:
        print(f"Error during CIK lookup: {e}")
        for company in companies:
            ciks[company] = "Error"

    max_company_length = max(len(company) for company in companies)
    cik_column_width = 15
    spacing = 25


    for company in companies:
        cik = ciks.get(company, "N/A")
        formatted_line = f"{company:<{max_company_length}}{' ' * spacing}{cik:<{cik_column_width}}"
        print(formatted_line)

    print("-----------------End of Company------------------------")


    start = time.time()
    c.find_common_holdings_multi_cik(tuple(['1350694', '1067983', '1037389', '0001350694']), "2024-11-13")
    # c.find_common_holdings_multi_cik(tuple(['1350694', '1067983', '1037389', '0001350694']))
    end = time.time()
    print("function timing test: "+ str(end - start))



