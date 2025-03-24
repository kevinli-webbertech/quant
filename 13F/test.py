import requests

r = requests.get("https://www.sec.gov/edgar/browse/?cik=0001350694")
print (r.text);



