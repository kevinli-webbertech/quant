from stock_api import *

## Blue chip

s = Stock("goog")

s.get_current_price()
s.daily_volume()
"""
get_current_price("msft")
get_current_price("aapl")
get_current_price("nvda")

## Rusessel
get_current_price("pltr") # Trump stock
get_current_price("nio") # Chinese E CAR
get_current_price("open") # AI in real estate

# food, industry

get_current_price("ko")

# ETF
get_current_price("voo") # vanguard sp500
get_current_price("xlf") # all finance sec
get_current_price("moat")  # finance+healthcare
get_current_price("schd") # high dividend sp500, 3%
get_current_price("spy") # state street sp500
get_current_price("gld") # state street gold ETF, gldm
"""