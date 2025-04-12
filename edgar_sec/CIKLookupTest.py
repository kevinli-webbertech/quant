import requests
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def CIKLookUp(company_names: list[str]):
  # needed to access sec edgar api/site
  user_agent = {'User-Agent': "testing111@gmail.com"}

  companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json",headers=user_agent)

  companyData = pd.DataFrame.from_dict(companyTickers.json(), orient='index')

  #fill all ciks with leading zeros for proper cik key 
  companyData['cik_str'] = companyData['cik_str'].astype(str).str.zfill(10)

  #Prints out the dataframe for the companydata (ticker, cik_key, and company title/name)
  #print(companyData)

  for company_name in company_names:
    #check to see if its one word (ticker) or multiple words (the company title name)
    if len(company_name.split()) == 1:
      company_name = company_name.upper()

      if not companyData[companyData['ticker'] == company_name].empty:
        #grabs first cik_str of row it sees
        cik_str = companyData[companyData['ticker'] == company_name]['cik_str'].iloc[0]
        print(f"{company_name}:{cik_str}")
      else:
        print(f"Ticker {company_name} not found.")
      
    else:
      
      if not companyData[companyData['title'] == company_name].empty:
        #grabs first cik_str of row it sees
        cik_str = companyData[companyData['title'] == company_name]['cik_str'].iloc[0]
        print(f"{company_name}:{cik_str}")
      else:
        print(f"Company {company_name} not found.")


  """
  This here jsut gives us the 13-F filing report (accession number - to access the holdings, report dates, and etc.) (if existS)
  
  #ubs group ag cik (Testing with)
  cik = '0001610520'

  getFilings = requests.get(
    f'https://data.sec.gov/submissions/CIK{cik}.json',
    headers=user_agent
    )

  companyFilings = pd.DataFrame.from_dict(getFilings.json()['filings']['recent'])

  companyFilings = companyFilings[companyFilings['form'] == 'quant_analysis-HR'][['accessionNumber', 'filingDate', 'form']]
  """
#Case senstitive if you want to use the company name/title, it is a lot easier to just use the ticker as input for CIKLookUp
print(CIKLookUp(['BHLB','Apple Inc.','UBS','META','COST',"AMERICAN EXPRESS CO","ABBOTT LABORATORIES"]))
