import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import pandas as pd
from bs4 import BeautifulSoup
import platform
from functools import lru_cache
import time
from SEC13F_util import *

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
    def __get_page_source(self, cik_key):
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
        driver.implicitly_wait(20)

        page_source = driver.page_source
        driver.quit()
        return page_source

    """
    finds first htm link on the sec gov page and then fetches it.
    It should be the latest 13F-HR filing.
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
    def find_stock_holdings(self, cik_key):
        page_source = self.__get_page_source(cik_key)
        if page_source is None:
            raise Exception("can't grab the initial html page.")

        soup = BeautifulSoup(page_source, "html.parser")

        response = requests.get(self.__find_htm_link(soup), headers=self.__headers__)

        if not response.status_code == 200:
            raise Exception("Failed to get the filing page")
        soup = BeautifulSoup(response.text, 'html.parser')

        date_div = soup.find('div', class_='formGrouping')
        filing_date = date_div.find('div', class_='info').get_text().strip()

        links = soup.find_all('a', href=True)
        # eg:
        # `url: https://www.sec.gov/Archives/edgar/data/1350694/000117266125000823/0001172661-25-000823-index.htm`
        infotable_links = [link.get('href') for link in links if link.get('href').endswith('.xml')]

        if not infotable_links or len(infotable_links) == 0:
            raise Exception("No XML files found.")

        # eg:
        # https://www.sec.gov/Archives/edgar/data/1350694/000117266125000823/infotable.xml
        latest_13f_filing_xml = infotable_links[-1]

        ### TODO: Need to break down from here to the end of this function and put it into aggregation_from_sec_xml(xml_url, filing_date)
        xml_doc_url = f"https://www.sec.gov{latest_13f_filing_xml}"

        print("\nlatest_13f_filing XML url:", xml_doc_url)

        xml_response = requests.get(xml_doc_url, headers=self.__headers__)
        xml_content = xml_response.text
        soup = BeautifulSoup(xml_content, 'xml')
        info_tables = soup.find_all('infoTable')

        data = []
        for info in info_tables:
            company_name = info.find('nameOfIssuer').text if info.find('nameOfIssuer') else 'None'
            total_value = int(info.find('value').text) if info.find('value') else 0
            shares_table = info.find('shrsOrPrnAmt')
            shares_owned = int(shares_table.find('sshPrnamt').text) if shares_table and shares_table.find('sshPrnamt') else 0

            data.append({'Company Name': company_name,
                        "Total Value": total_value,
                        "Shares Owned": shares_owned,
                        "Filing Date": filing_date
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

    import time
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd

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
        print(company_name)

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

    ## Darren can you see if you can fill this up
    def company_name_lookup(company_name:str):
        pass

    """
    Finds overlapping stocks based on *args number of stock dataframes placed into the parameter
    Make sure you use the find_stock_holdings() function to generate stock holding dataframes and 
    input them into this function.
    
    Example: 
        c = SEC13F()
        c.find_common_holdings_multi_cik(tuple(['1350694', '1067983', '1037389', '1610520']))
        
    Output: A list of company names, displayed vertically.
    """
    def find_common_holdings_multi_cik(self, list_of_ciks):
        if len(list_of_ciks) == 0:
            raise Exception("Invalid input, please check function definitions.")

        data_frames = []
        for cik in list_of_ciks:
           #company_name = self.company_name_lookup(cik)
           data_frames.append(self.find_stock_holdings(cik))
        same_holdings = aggregate_holdings(data_frames)

        # TODO Print all original names of the company from CIK
        # company_names = cik_lookup(list_of_ciks)

        print("\n------------------Shared Stock Holdings---------------------")
        shared_holdings = same_holdings.split(",")
        for holding in shared_holdings:
            print(holding.strip())
        print("\n------------------End Stock Holdings---------------------")


if __name__ == "__main__":
    c = SEC13F()

    companies = ['BHLB','Apple Inc.','UBS','META','COST',"AMERICAN EXPRESS CO","ABBOTT LABORATORIES "]
    for company in companies:
        print(c.cik_lookup(company))

    start = time.time()
    c.find_common_holdings_multi_cik(tuple(['1350694', '1067983', '1037389', '1610520']))
    end = time.time()
    print("function timing test:"+ str(end - start))


    #c.aggregation_from_sec_xml("https://www.sec.gov/Archives/edgar/data/1350694/000117266125000823/infotable.xml")

    #start = time.time()
    #c.find_common_holdings_multi_cik(tuple(['1350694', '1067983', '1037389', '1610520']))
    #end = time.time()
    #print("function timing test:"+ str(end - start))
   
   
   # c.aggregation_from_sec_xml("https://www.sec.gov/Archives/edgar/data/1067983/000095012324011775/infotable.xml")


