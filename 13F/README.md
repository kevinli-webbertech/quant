# 13F Database

---------------------------------------------
The database supports financial analysis and investment research by storing and organizing data on 13F stock holdings of 
institutions/companies. It allows users to track company ownership trends, analyze investment strategies, and monitor regulatory 
filings efficiently.
---------------------------------------------

## How to run the code

### Step 1 install python package

* `pip3 install selenium`
* `pip3 install pandas`
* `pip3 install bs4`
* `pip3 install lxml`

In ubuntu, run the following,

`sudo apt install chromium-chromedriver`

### Test driver

The above driver is a binary,

```shell
(base) xiaofengli@xiaofenglx:~/git/webbertech_site/quant_analysis/edgar_sec$ chromedriver
Starting ChromeDriver 133.0.6943.53 (9a80935019b0925b01cc21d254da203bc3986f04-refs/branch-heads/6943@{#1389}) on port 0
Only local connections are allowed.
Please see https://chromedriver.chromium.org/security-considerations for suggestions on keeping ChromeDriver safe.
ChromeDriver was started successfully on port 36357.
(base) xiaofengli@xiaofenglx:~/git/webbertech_site/quant_analysis/edgar_sec$ which chromedriver
/usr/bin/chromedriver
```

Run `headless_chrome_driver_test.py` and make sure you don't see any crash or errors.

### Step 2 Run `13F.py`

## CIK

Stores information about companies that have investment holdings reported in 13F filings.
Each company is uniquely identified by a CIK (Central Index Key), a 10-digit identifier assigned by the SEC.

## lru_cache

Cache is added for experimental usage, but I do not have enough time to see if it makes a difference in timing.

## Business Logic

This system is more like the `https://hedgefollow.com/13f`. It provides,

* Database to take snapshot of certain companies, not all [only those to our interests].
* From the DB SQL query we can check from last filing and the latest filing, regarding each stock whether it is increasing shares or decreasing. [we are not providing external financial service like the hedgefollow]
* CLI: We provide certain functions, which later on, we will restrict which functiosn is internal functions such as the private functions in Java so that only certain functions can be called CLI.
* A simple web interface to show us some aggregation using reactjs + typescript.

Tip: coding we will extensively using chatGPT or grok3, not type or write by hand. Our job is to stich the code quickly and test it and send PR.

As a new generation of computer programming or IT professional we would like to increase our learning rate to produce IT products and artifacts.

### Task1 Just test the following API and see if it is good or not

**Use CIK Lookup API from python package** (Don't do this yet)
https://sec-edgar.github.io/sec-edgar/about.html

Please see `CIKLookupTest.py`, and we find it is actually parsing the following json file.

Question: Can we just use it without redesign the wheel.

### Task2 Design our own cik lookup

If the answer is no, we do not want to fix their package, we would just write our own by `piggyback` their code and improve it.

https://www.sec.gov/files/company_tickers.json

### Task3: Write another Util function with Pandas (yangyang)

**https://www.sec.gov/Archives/edgar/data/1067983/000095012325002701/xslForm13F_X02/39042.xml** (High priority)

Just pandas import the above link, aggregate using groupBy companies on columns 4 and 5.
Verify total holding and total value of each stock of the top 5 using third party website or resources.
Try to understand 13F format.

import pandas as pd

# Define the SEC 13F XML file URL
xml_url = "https://www.sec.gov/Archives/edgar/data/1067983/000095012325002701/xslForm13F_X02/39042.xml"

# Read XML data
df = pd.read_xml(xml_url)

df_grouped = df.groupby("name")[["value", "shrsOrPrnAmt"]].sum().reset_index()

# Display the top 5 holdings
df_grouped = df_grouped.sort_values(by="value", ascending=False).head(5)

print(df_grouped)

**https://www.sec.gov/files/company_tickers.json** (check the following ids are findable)

1350694,1037389,1610520

Worse scenario, manual lookup.

### Task4: Try to write to db. (Darren)

@Darren, just finish the db code by using chatGPT, and quickly shove in some code to make it work.
Then we can take snapshot to store the latest filing to the database.
The snapshot should be based on the latest filing as of now.

### Task5: Take a snapshot in both Python display/print and DB writing base on parameter of filing date. (Fix by Yangyang based on task4's Darren's work)

https://www.sec.gov/edgar/browse/?cik=1350694

@Yangyang, right now the html scraping is to grab the latest. We would need to make this part a bit more smarter.

We will be able to grab any arbiturary snapshot of filing, based on the filing date.

### Task6: (Display improvement on CLI, yangyang)

This is our current display for common sharing from multi institutions.
We would like to display a few more columns, of each of these institutions and their total holdings and shares of the
of shares.

```shell
------------------Shared Stock Holdings---------------------
NVR INC
CAPITAL ONE FINL CORP
CITIGROUP INC
APPLE INC
LENNAR CORP
CONSTELLATION BRANDS INC
CHEVRON CORP NEW
LOUISIANA PAC CORP
AON PLC
VERISIGN INC
VISA INC
KROGER CO
COCA COLA CO
ALLY FINL INC
DOMINOS PIZZA INC
MOODYS CORP
CHARTER COMMUNICATIONS INC N

------------------End Stock Holdings---------------------
```

Expected to see the following,

```
Stock/ETF                    CIK1 [company_name2]                 CIK2[company_name2]         .....
NVR INC
CAPITAL ONE FINL CORP
CITIGROUP INC
APPLE INC
LENNAR CORP
CONSTELLATION BRANDS INC
CHEVRON CORP NEW
LOUISIANA PAC CORP
AON PLC
VERISIGN INC
VISA INC
KROGER CO
COCA COLA CO
ALLY FINL INC
DOMINOS PIZZA INC
MOODYS CORP
CHARTER COMMUNICATIONS INC N
```

This is a simple output DF blending and added column headers...etc.

## Task 7 Finance research (asset size, decreasing order we need to find out how to find that list from 13F websites or documentations. Assignee: yangyang)

Let us assume, 13F filers, who had AUM more than 100M, there are 8000 -10K companies filing.
Who are they, can we get a decreasing order to see who they are. (tops 50s, their performance. -- finance question)

For example, `H&H International Investment`.
* https://www.sec.gov/files/company_tickers.json
* https://hedgefollow.com/13f
* https://hedgefollow.com/funds/H-And-H+International+Investment+LLC

>Hint: notes from Kevin, I actually found the following link,

- https://www.sec.gov/cgi-bin/browse-edgar?company=&CIK=&type=13F&owner=include&count=100&action=getcurrent

- https://www.sec.gov/files/form_13f.pdf
- https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets (zip of csv) - Maybe this is the place to get all the companies name and CIKs.

But I can only see 100 entries at most, not sure if we can hack the API or they offer some other APIs that can pull all the companies names.


## 3 Characters of Information

* Asymmetric, I know, you don't know and I am rich.
* Realtime feature. 
* Historic feature. Give me the last 150 yr of DOWS, and what is the pattern. Pattern on the left. Data cost money.

Extra, the data might not be the raw it might be some insight, data analysis or big data analysis.
Analyzed data already.

>Hint:
> * Google search(raw data, cached web crawler stuff from your websites and DNS servers), build into index for quick search. 
> * ML/deepseak/OpenAI/Grok3, raw model + curated structured raw data -> trained model(huge, TB or GB)
> * Database (can be huge, but also file, had B tree indexed, just like google search using column-based db as well.) vs trained model (file)

## Ref

- https://www.sec.gov/submit-filings/filer-support-resources/how-do-i-guides/look-central-index-key-cik-number
- https://www.sec.gov/search-filings/cik-lookup
- https://www.edgarcompany.sec.gov/