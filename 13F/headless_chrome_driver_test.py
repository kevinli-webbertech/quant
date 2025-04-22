from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure headless Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('user-data-dir=/tmp/chrome_headless')

# Launch headless Chrome
driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=chrome_options)

# Navigate to a website and perform test actions
driver.get("https://www.sec.gov/edgar/browse/?cik=1350694")

# ... perform test actions on the page using Selenium commands
driver.quit()