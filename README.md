# Stock Analysis Website

### Description:
#### **CS50x Final Project**
A web-based stock analysis application built with Flask, inspired by platforms like Yahoo Finance and Morningstar. The web lets users look up stocks, view the price chart (tradingview), look up the financial statements, track key metrics, keep updated by the most recent related news, and manage a personal watchlist.

#### **Website Features**
- Market News - General financial news feed
- Watchlist - Add/remove stocks to a personal watchlist with live price updates
- User Authentication - Register, login, logout with hashed passwords
- Stock Quote Page - consist of 4 tab, summary, income, balance, and cashflow
    - Financial Statements - Multi-year Income Statement, Balance Sheet, and Cash Flow Statement in tabbed view
    - Summary - Consist of stock chart, stock related news, trading info, key metrics, and financial ratio
    - Key Metrics & Ratios - ROA, ROE, ROIC, FCF, GPM, OPM, NPM, Current Ratio, DER, PER, PBV
    - Trading info - Live price, change percentage, and market cap
    - TradingView Chart - Interactive price chart embedded on every stock page
    - Company News - Recent company news
    - Watchlist Button - To add the current viewed stock to watchlist

#### **Language Used**
Python, SQLite, HTML, CSS, Javascript

#### **Imports Used**
Flask, cs50, Flask-Session, requests, python-dotenv


#### **Tech Stack**
| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Templating | Jinja2 |
| Database | SQLite (via CS50 `SQL`) |
| Frontend | Bootstrap 5, TradingView Widget |
| APIs | Financial Modeling Prep (FMP), Finnhub, Twelve Data |
| Auth | Werkzeug password hashing, Flask-Session |

#### **API Used**
the API used in this project are :
- **Financial Modeling Prep (FMP)**, FMP is used to get all the financial and market data for this project.
- **Finnhub**, Finnhub is used to get all the news, general economics and some specific stocks related.
- **Twelve Data**, Twelve data is used to download/update all current listed stocks in the market to the database, so the program can check if the quote/stock truly exists and correct through the database.

#### **Project Structure**
```
week_10/
├── app.py              # Main Flask application and routes
├── addition.py         # Helper functions (apology, login_required, fetch_data)
├── stock_up.py         # Script to populate the stocks table from Twelve Data API
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed)
├── finance.db          # SQLite database
├── static/
│   └── styles.css
└── templates/
    ├── layout.html
    ├── index.html      # Watchlist (home page)
    ├── quote.html      # Stock detail page
    ├── news.html       # Market news
    ├── login.html
    ├── register.html
    └── apology.html
```

#### **More Detailed Explanation about Files**
- **app.py**, main Flask application, consists of 8 routes:
    - ("/"), process the data from the watchlist table and use the FMP API to get the trading info.
    - ("/login"), used to log in the user and set the session.
    - ("/logout"), used to log out the user and clear the session.
    - ("/register"), used to register the user and set the session when the user successfully registers.
    - ("/quote"), process the input from the user in the stock/quote searchbar and show the stock's detailed page. The composite search bar is optional, by default the program would automatically try to search for a stock based on what is filled in the quote search bar and in the database of stocks. The composite is mostly used to make the search more specific, for example, some companies from different markets may have the same quote/symbol, so to differentiate them, you would need to specify the composite of the stocks. The financial data/information is obtained from the FMP API, while the news data is obtained from Finnhub.
    - ("/news"), used to get all the general economic news.
    - ("/add_watchlist"), used to add a stock to watchlist.
    - ("/remove_watchlist"), used to remove a stock from watchlist.
- **addition.py**, consit of helper functions (apology, login_required, fetch_data)
    - apology function, used for the apology or error page.
    - login_required, so that a certain function can only run/function if the user has already logged in.
    - fetch_data, function to fetch the data from API.
- **stock_up.py**, consists of a function used to download or update the list of stocks that exist in the current market to the database.

#### **Notes from Creator**

- **Create your `.env` file**
    ```
    FMP_API_KEY=your_fmp_key_here
    FH_API_KEY=your_finnhub_key_here
    TD_API_KEY=your_twelvedata_key_here
    ```

    You can get free API keys from:
    - [Financial Modeling Prep](https://financialmodelingprep.com/)
    - [Finnhub](https://finnhub.io/)
    - [Twelve Data](https://twelvedata.com/)

- **Populate / Update of the stock list** is done manually
    ```
    python stock_up.py
    ```
    
- **FMP free tier**, Financial statements and key metrics are only available for a limited set of US-listed stocks.
- **Finnhub free tier**, Company news for non-US stocks (e.g. IDX) may be limited or unavailable.
- **Stock search** validates input against the local stocks table populated by stock_up.py, so no unnecessary API calls are made for invalid symbols.
- **No real-time streaming**, prices update on page load only.
- **New Database**, Before submitting or uploading this project, I already clear all the data from the database, so it's a fresh new database.
