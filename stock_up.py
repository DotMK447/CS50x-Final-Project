# To update the stock list in finance.db
# used to download the stocks that is currently listed (manual)

import requests
from cs50 import SQL
from dotenv import load_dotenv
import os

db = SQL("sqlite:///finance.db")
load_dotenv()
API_KEY_TD = os.getenv("TD_API_KEY")

url = "https://api.twelvedata.com/stocks"
params = {"apikey": API_KEY_TD}
response = requests.get(url, params=params)
data = response.json()

for stock in data["data"]:
    db.execute(
        "INSERT OR IGNORE INTO stocks (symbol, name, exchange) VALUES (?, ?, ?)",
        # Insert a new row into the table "stocks", BUT if it already exists, ignore it instead of throwing an error, because symbol is UNIQUE, duplicates are not allowed.
        stock["symbol"],
        stock["name"],
        stock["exchange"]
    )

print("Stock list downloaded!")

