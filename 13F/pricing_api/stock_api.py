import yfinance as yf

"""
 This project is to help us quickly get some logic implemented for stock analysis.
 This is the foundation of the quantum research.
 We will implement varieties of the following,
 
   * Stock analyzer
   * Stock evaluation and rating
   * Customized stock indicator
   * Backend engine for our own stock watching system (db of course, not whole lot, we would need to test out sqlite for 3000 stocks and see db performance)
   * Backtesting tools for an system to emulate buy and sell and setup initial fund $ amount to emulate our strategies.
   * An alert system that is running on AWS EC2 VM or my in-house server to send emails to us when an interesting event 
     happening such as crashing or certain stocks are at certain price point.
   
   Code: We would use AI tools as much as possible and use our own human reading and judgements.    
"""

## The most useful information will be written to our stock evaluation system.

class Stock:
    __stock_data = None
    __ticker = None

    def __init__(self, ticker):
        self.__stock_data = yf.Ticker(ticker)
        self.__ticker = ticker

    def get_current_price(self):
        current_price = self.__stock_data.info['regularMarketPrice']
        print(f"Current price of {self.__ticker}: {current_price}")

    def daily_volume(self):
        # Get historical market data
        hist = self.__stock_data.history(period="1d")  # "1d" for the last day
        # Extract the trading volume
        trading_volume = hist['Volume'].iloc[0]
        print(f"Trading Volume for {self.__ticker} on the last trading day: {trading_volume}")

    def volume_date_range(self, ticker, start_date, end_date):
        hist = self.__stock_data.history(start=start_date, end=end_date)

        # Extract the trading volume for the date range
        trading_volume = hist['Volume']

        # Print the trading volume for each day in the range
        print(f"Trading Volume for {ticker} from {start_date} to {end_date}:")
        print(trading_volume)

    def fast_info(self):
        print(self.__stock_data.fast_info)

    def dividends(self):
        print(self.__stock_data.dividends)

    def splits(self):
        print(self.__stock_data.splits)

    def balance_sheet(self):
        print(self.__stock_data.balancesheet)

    def actions(self):
        print(self.__stock_data.actions)

    def cash_flow(self):
        print(self.__stock_data.cash_flow)

    def analyst_price_targets(self):
        print(self.__stock_data.analyst_price_targets)

    def funds_data(self):
        print(self.__stock_data.funds_data)


