from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from addition import apology, login_required, fetch_data
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from datetime import date, timedelta
import requests
import os

#flask
app = Flask(__name__)

#Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

BASE_URL_FMP = "https://financialmodelingprep.com/stable"
load_dotenv()
API_KEY_FMP = os.getenv("FMP_API_KEY")
API_KEY_FH = os.getenv("FH_API_KEY")

@app.route("/")
@login_required
def watchlist():
    rows = db.execute("SELECT symbol FROM watchlist WHERE user_id = ?", session["user_id"])
    stocks = []
    for row in rows:
        quote_url = "https://financialmodelingprep.com/stable/quote"
        FS_params = {
            "symbol": row["symbol"],
            "apikey": API_KEY_FMP,
        }
        response = fetch_data(quote_url, FS_params)
        if response:
            raw = response[0]
            change = float(raw["changePercentage"])
            # create a NEW object (important!)
            stock = {
                "symbol": raw["symbol"],
                "price": raw["price"],
                "changePercentage": change,
                "exchange": raw["exchange"],
            }
            # assign color
            if change > 0:
                stock["color"] = "text-success"
            elif change < 0:
                stock["color"] = "text-danger"
            else:
                stock["color"] = "text-secondary"
            stocks.append(stock)

    return render_template("index.html", stocks=stocks)


# get to get to the pages, post to get the input or answer.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        req
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Login successful", "success")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        verify = request.form.get("verify_password")
        if not password or not username or not verify:
            return apology("missing input")
        elif password != verify:
            return apology("password not match")
        elif db.execute("SELECT * FROM users where username = ?", username):
            return apology("username is already used")
        else:
            db.execute("insert into users (username, hash) values(?, ?)", username, generate_password_hash(password))
            # to get value id from list of dictionary id, [{"id": value(kek 89)}]
            session["user_id"] = db.execute("select id from users where username = ?", username)[0]["id"]
            flash("You are registered", "success")
            return redirect("/")
    else:
        return render_template("register.html")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        stock = request.form.get("quote").upper()
        composite = request.form.get("composite").upper()
        if composite:
            stock_list = db.execute("select * from stocks where symbol = ? and exchange = ?", stock, composite)
        else:
            stock_list = db.execute("select * from stocks where symbol = ?", stock)
        exchange = db.execute("select exchange from stocks where symbol = ?", stock)
        if not stock or not stock_list:
            return apology("stock not found")
        else:
            #GET NEWS, stocks outside of US aren't accesible due to the use of free version.
            today = date.today()
            past = today - timedelta(days=7)

            news_url = "https://finnhub.io/api/v1/company-news"
            if composite == "IDX":
                symbol = stock + ".JK"
            else:
                symbol = stock
            news_params = {
            "symbol": symbol,
            "from": past.strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d"),
            "token": API_KEY_FH
            }
            news_response = requests.get(news_url, params=news_params)
            if news_response.status_code == 200:
                news = news_response.json()
            else:
                print("Error:", news_response.status_code)
                news = []

            #Financial statement (only for some US stocks due to the use of free version)
            income_metrics = {
                "Year": "fiscalYear",
                "Revenue": "revenue",
                "Cost of revenue": "costOfRevenue",
                "Gross Profit": "grossProfit",
                "Research and Development Expenses": "researchAndDevelopmentExpenses",
                "General and Administrative Expenses": "generalAndAdministrativeExpenses",
                "Selling and Marketing Expenses": "sellingAndMarketingExpenses",
                "Selling, General, And Administrative Expenses":"sellingGeneralAndAdministrativeExpenses",
                "Other Expenses":"otherExpenses",
                "Operating Expenses":"operatingExpenses",
                "Operating Income":"operatingIncome",
                "Non Operating Income Excluding Interest": "nonOperatingIncomeExcludingInterest",
                "EBIT": "ebit",
                "Total Other Income Expenses Net": "totalOtherIncomeExpensesNet",
                "Income Tax Expense": "incomeTaxExpense",
                "Net Income": "netIncome",
                "EPS": "eps",
            }
            BS_metrics = {
                "Year": "fiscalYear",
                "Assets": None,
                "Cash and Cash Equivalents": "cashAndCashEquivalents",
                "Short Term Investments": "shortTermInvestments",
                "Cash and ShortTerm Investments": "cashAndShortTermInvestments",
                "Net Receivables": "netReceivables",
                "Accounts Receivables": "accountsReceivables",
                "Other Receivables": "otherReceivables",
                "Inventory": "inventory",
                "Prepaids": "prepaids",
                "Other Current Assets": "otherCurrentAssets",
                "Total Current Assets": "totalCurrentAssets",
                "PPE": "propertyPlantEquipmentNet",
                "Goodwill": "goodwill",
                "Intangible Assets": "intangibleAssets",
                "Goodwill and IntangibleAssets": "goodwillAndIntangibleAssets",
                "longTerm Investments": "longTermInvestments",
                "Tax Assets": "taxAssets",
                "Other NonCurrent Assets": "otherNonCurrentAssets",
                "Total NonCurrent Assets": "totalNonCurrentAssets",
                "Other Assets": "otherAssets",
                "Total Assets": "totalAssets",
                "Liabilities": None,
                "Total Payables": "totalPayables",
                "Account Payables": "accountPayables",
                "Other Payables": "otherPayables",
                "Accrued Expenses": "accruedExpenses",
                "ShortTerm Debt": "shortTermDebt",
                "Capital Lease Obligations Current": "capitalLeaseObligationsCurrent",
                "Tax Payables": "taxPayables",
                "Deferred Revenue": "deferredRevenue",
                "Other Current Liabilities": "otherCurrentLiabilities",
                "Total Current Liabilities": "totalCurrentLiabilities",
                "LongTerm Debt": "longTermDebt",
                "Deferred Revenue NonCurrent": "deferredRevenueNonCurrent",
                "Deferred Tax Liabilities NonCurrent": "deferredTaxLiabilitiesNonCurrent",
                "Other NonCurrent Liabilities": "otherNonCurrentLiabilities",
                "Total NonCurrent Liabilities": "totalNonCurrentLiabilities",
                "Other Liabilities": "otherLiabilities",
                "Capital Lease Obligations": "capitalLeaseObligations",
                "Total Liabilities": "totalLiabilities",
                "Equity": None,
                "Treasury Stock": "treasuryStock",
                "Preferred Stock": "preferredStock",
                "Common Stock": "commonStock",
                "Retained Earnings": "retainedEarnings",
                "Additional Paid In Capital": "additionalPaidInCapital",
                "Accumulated Other Comprehensive Income Loss": "accumulatedOtherComprehensiveIncomeLoss",
                "Other Total Stockholders Equity": "otherTotalStockholdersEquity",
                "Total Stockholders Equity": "totalStockholdersEquity",
                "Total Equity": "totalEquity",
                "Total Liabilities and Total Equity": "totalLiabilitiesAndTotalEquity",
            }

            CF_metrics = {
                "Year": "fiscalYear",
                "Cash Flow from Operating Activities": "netCashProvidedByOperatingActivities",
                "Cash Flow from Investing Activities": "netCashProvidedByInvestingActivities",
                "Cash Flow from Financing Activities": "netCashProvidedByFinancingActivities",
                "Cash at Beginning of Period": "cashAtBeginningOfPeriod",
                "Cash at End of Period": "cashAtEndOfPeriod",
                "Net Change in Cash": "netChangeInCash",
                "capital Expenditure":"capitalExpenditure",
                "FCF": "freeCashFlow",

            }

            # Quote
            quote_url = "https://financialmodelingprep.com/stable/quote"
            # Income statement
            income_url = "https://financialmodelingprep.com/stable/income-statement"
            # Balance sheet
            balance_url = "https://financialmodelingprep.com/stable/balance-sheet-statement"
            # Cashflow
            cashflow_url = "https://financialmodelingprep.com/stable/cash-flow-statement"
            # Key Metrics
            kmetrics_url = "https://financialmodelingprep.com/stable/key-metrics"
            # Financial Ratios
            fratio_url =  "https://financialmodelingprep.com/stable/ratios"

            FS_params = {
            "symbol": stock,
            "apikey": API_KEY_FMP,
            }
            quote = fetch_data(quote_url, FS_params)
            income = fetch_data(income_url, FS_params)
            balance = fetch_data(balance_url, FS_params)
            cashflow = fetch_data(cashflow_url, FS_params)
            keymetrics = fetch_data(kmetrics_url, FS_params)
            fratio = fetch_data(fratio_url, FS_params)
            return render_template("quote.html", stock=stock, composite=composite, exchange=exchange, news=news, quote=quote, income=income, balance=balance, cashflow=cashflow,
                                   keymetrics=keymetrics, fratio=fratio, income_metrics=income_metrics, BS_metrics=BS_metrics, CF_metrics=CF_metrics)
    else:
        return redirect("/")


@app.route("/news")
@login_required
def news():
    url = "https://finnhub.io/api/v1/news"
    params = {
        "category": "general",
        "token": API_KEY_FH
    }
    try:
        response = requests.get(url, params=params)
        articles = response.json()
    except:
        articles = []
    return render_template("news.html", articles=articles)

@app.route("/add_watchlist", methods=["POST"])
@login_required
def add_watchlist():
    symbol = request.form.get("symbol").upper()
    existing = db.execute(
    "SELECT * FROM watchlist WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
    if not existing:
        db.execute("INSERT INTO watchlist (user_id, symbol) VALUES (?, ?)", session["user_id"], symbol)
        flash("Stock added to Watchlist", "success")
    else:
        flash("Stock already in the Watchlist", "error")
    return redirect("/")


@app.route("/remove_watchlist", methods=["POST"])
@login_required
def remove_watchlist():
    symbol = request.form.get("symbol").upper()
    db.execute("DELETE FROM watchlist WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
    flash("removed from Watchlist", "success")
    return redirect("/")
