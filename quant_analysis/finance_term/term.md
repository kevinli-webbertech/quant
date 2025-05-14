# ARR (Account Rate of Return)
### ARR = Average Annual Profit / Initial Investment
ARR does not consider the time value of money or cash flow, which can be an integral part of maintaining a business

ARR is a capital budgeting metric that is helpful if you want to calculate an investment's profitability quickly

### Calculation Method
* It is net profit
* If the investment is property, plant, and equipment (PP&E), it still needs to subtract depreciation expense to achieve net profit
* The division will yield a decimal, so it is optimal to multiply 100 to get it as percentage

# EBITDA – Earnings Before Interest, Taxes, Depreciation, and Amortization
### Definition: Measures operating performance excluding non-cash charges and capital structure.
### Formula: EBITDA = Net Income + Interest + Taxes + Depreciation + Amortization

Pros:
* Removes accounting/tax variation.
* Used to compare firms across industries or geographies.

Cons:
* Excludes CapEx — may overstate cash flow.
* Not GAAP-compliant; may vary in calculation.
* Misleading for asset-heavy companies or firms with high debt loads.

# EBIT – Earnings Before Interest and Taxes
### Definition: Operating income from core business before financing or tax impact.

### Formula: 
* EBIT = Revenue – Operating Expenses (excluding interest and taxes) 
* EBIT = Net Income + Interest + Tax

Usage: Used in EV/EBIT valuation, especially in capital-intensive sectors.

Pros: 
* GAAP-compliant. 
* Includes depreciation, making it more reflective than EBITDA.

Cons:
* Still excludes tax structure and interest burden, which can be relevant.

# RSU - Restricted Stock Unit
### Definition: A form of equity compensation where employees receive company shares subject to vesting.
* RSUs are issued to an employee in the form of company shares through a vesting plan and a distribution schedule after achieving required performance milestones or upon remaining with their employer for a particular length of time.

* RSUs are restricted during a vesting period that may last several years during which they cannot be sold. Once vested, RSU is just common stock to sell.

* Unlike stock options or warrants which may expire worthless, RSU will always have some values based on the market price and underlying values.

Pros: Aligns employee interest with shareholders.

Cons: Can dilute equity. Taxable even if shares are not sold.

# ADR - American Depository Receipts
### Definition: A negotiable security that represents shares in a foreign company, traded on U.S. exchanges.
Structure:
* Issued by U.S. banks.
* Backed by actual shares held in custody in the foreign company’s home country.

Types:
* Level I (OTC, least regulated)
* Level II & III (listed on NYSE/NASDAQ with SEC compliance)

Pros:
* Enables U.S. investors to invest in foreign firms easily.
* Priced in USD, pays dividends in USD.

Cons:
* Currency risk.
* Not always fully reflective of local stock price due to time zone or regulatory lag.

# GDR – Global Depositary Receipt
### Definition: Similar to ADR but used for listing foreign shares on multiple global exchanges (e.g., London, Frankfurt, Luxembourg).
Issuer: Typically used by non-U.S. companies raising capital internationally.

Currency: Usually USD or Euro.

Notes: More common in Europe, Asia, and emerging markets.

# REIT – Real Estate Investment Trust
### Definition: A company that owns, operates, or finances income-producing real estate and is required to distribute 90%+ of taxable income to shareholders.
Types:
* Equity REITs (own properties)
* Mortgage REITs (hold debt instruments)
* Hybrid REITs

Use Case: Popular among income-focused investors.

Pros:
* Tax Advantage: Avoids double taxation; dividends are taxed only at the investor level.

Cons:
* Sensitive to interest rates.
* High payout means limited reinvestment into growth.

# ETN – Exchange-Traded Note (Need dive deeper)
### Definition: An unsecured debt security issued by banks that tracks an underlying index or asset class.
Structure:
* No ownership in underlying assets.
* Return is linked to the performance of the index, minus fees.

Pros:
* Tax-efficient (no interest or dividend distributions).
* Access to hard-to-replicate markets (e.g., volatility).

Cons:
* Credit risk of issuing bank.
* Lower liquidity than ETFs.

# CBOE – Chicago Board Options Exchange
### Definition: The largest U.S. options exchange, specializing in equity, index, and ETF options.
Significance:
* Pioneer of standardized options contracts.
* Operates VIX (Volatility Index), a key market fear gauge.

Indexes:
* CBOE VIX: Measures implied volatility from S&P 500 options.
* CBOE SKEW: Tracks tail-risk of extreme market moves.

Products: Options, futures, volatility derivatives.

# ITM (In the Money) / OTM (Out of the Money)
### In the Money (ITM):
* Call Option: Stock Price > Strike Price.
* Put Option: Stock Price < Strike Price.
* Has intrinsic value.
### Out of the Money (OTM):
* Call: Stock Price < Strike Price.
* Put: Stock Price > Strike Price.
* No intrinsic value; only time value.

# The Greeks in Finance

### Delta (Δ)
* Measures sensitivity of an option’s price to a $1 change in the underlying asset.
* Range: 0 to 1 for calls; 0 to –1 for puts.
* Example: Delta = 0.6 → option value rises 0.60 cent if stock rises 1 dollar.

### Theta (θ)
* Measures time decay — how much an option loses value as expiration approaches.
* Usually negative; larger for near-the-money options.
* Example: Theta = –0.03 → loses 0.03 cent per day.

### Gamma (Γ)
* Measures the rate of change of Delta.
* High gamma = delta changes rapidly → relevant for hedging.

### Vega (ν)
* Measures sensitivity to changes in implied volatility.
* Example: Vega = 0.2 → option gains $0.20 if IV rises 1%.

### Rho (ρ)
* Measures sensitivity to interest rate changes.
* Example: Rho = 0.1 → option gains 0.10 cent if rates rise 1%.

### Alpha (α)
* Measures excess return vs. benchmark (active return).
* Formula: Alpha = Portfolio Return – Expected Return (per CAPM)

### Beta (β)
* Measures volatility vs. market.
* Beta > 1 → more volatile than market.
* Formula: Beta = Cov(Ri, Rm) / Var(Rm)


# Basic Ratio
| Metric           | Formula / Definition                 | Usage & Notes                                         |
| ---------------- | ------------------------------------ | ----------------------------------------------------- |
| EPS              | Net Income / Shares Outstanding      | Core profitability measure per share                  |
| P/E Ratio        | Share Price / EPS                    | Valuation based on earnings (growth vs. value stocks) |
| P/B Ratio        | Share Price / Book Value per Share   | Compares market value to accounting value             |
| ROE              | Net Income / Shareholder Equity      | Measures return on equity capital                     |
| ROA              | Net Income / Total Assets            | Measures return on all assets                         |
| Dividend Yield   | Annual Dividend / Share Price        | Income-focused metric                                 |
| Current Ratio    | Current Assets / Current Liabilities | Liquidity measure (short-term obligations)            |
| Debt-to-Equity   | Total Debt / Shareholder Equity      | Leverage risk indicator                               |
| Free Cash Flow   | Operating Cash Flow – CapEx          | True cash generation post-investment                  |
| Market Cap       | Share Price × Shares Outstanding     | Company size measurement                              |
| Enterprise Value | Market Cap + Debt – Cash             | Used in EV multiples; reflects total takeover cost    |

# Basic Multiples
| Metric     | Description                     | Best Used For                   |
| ---------- | ------------------------------- | ------------------------------- |
| EV/EBITDA  | Core operating profit           | Most common for M\&A and PE     |
| EV/Sales   | Revenue-based; pre-profit firms | High-growth startups or SaaS    |
| P/E        | Price per dollar of earnings    | General valuation               |
| PEG        | P/E divided by earnings growth  | Growth-adjusted valuation       |
| Book Value | Accounting equity per share     | Useful in finance-heavy sectors |

