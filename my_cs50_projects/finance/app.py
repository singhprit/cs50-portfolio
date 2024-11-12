import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Get user's cash balance
    user_data = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    cash = user_data[0]["cash"]

    # Get user's stock holdings
    holdings = db.execute("""
        SELECT symbol, SUM(shares) AS shares
        FROM transactions
        WHERE user_id = ?
        GROUP BY symbol
        HAVING SUM(shares) > 0
    """, session["user_id"])

    # Add current stock price and total for each holding
    for holding in holdings:
        stock = lookup(holding["symbol"])
        holding["name"] = stock["name"]
        holding["price"] = stock["price"]
        holding["total"] = holding["shares"] * stock["price"]

    # Calculate grand total (cash + total value of stocks)
    grand_total = cash + sum(holding["total"] for holding in holdings)

    return render_template("index.html", cash=cash, holdings=holdings, grand_total=grand_total)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        # Get symbol and shares from form
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate symbol and shares
        if not symbol:
            return apology("must provide stock symbol", 400)
        elif not shares.isdigit() or int(shares) <= 0:
            return apology("must provide positive integer shares", 400)

        # Lookup stock price
        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)

        # Calculate total cost
        price = stock["price"]
        total_cost = price * int(shares)

        # Check if user has enough cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        if user_cash < total_cost:
            return apology("can't afford", 400)

        # Deduct cash and record transaction
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", total_cost, session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   session["user_id"], symbol, int(shares), price)

        flash("Bought!")
        return redirect("/")
    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ?", session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Get stock symbol
        symbol = request.form.get("symbol")

        # Lookup stock
        stock = lookup(symbol)
        if stock is None:
            return apology("invalid stock symbol", 400)

        # Show quoted price
        return render_template("quoted.html", stock=stock)
    else:
        return render_template("quote.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # If user submits the form via POST
    if request.method == "POST":
        # Get form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate form data
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        # Check if username already exists
        try:
            # Hash the password for secure storage
            hash_password = generate_password_hash(password)
            # Insert new user into database
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)
        except:
            # If insertion fails (likely due to unique constraint on username)
            return apology("username already exists", 400)

        # Redirect user to login page after successful registration
        flash("Registered successfully! Please log in.")
        return redirect("/login")

    # If user reached route via GET, display the registration form
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        # Get symbol and shares from form
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Validate input
        if not symbol:
            return apology("must select a stock to sell", 400)
        elif not shares.isdigit() or int(shares) <= 0:
            return apology("must provide positive integer shares", 400)

        # Check if user has enough shares to sell
        user_shares = db.execute("SELECT SUM(shares) AS shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol",
                                 session["user_id"], symbol)[0]["shares"]
        if user_shares < int(shares):
            return apology("too many shares", 400)

        # Lookup stock price
        stock = lookup(symbol)
        price = stock["price"]
        total_value = price * int(shares)

        # Update database: add cash and record sale
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_value, session["user_id"])
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   session["user_id"], symbol, -int(shares), price)

        flash("Sold!")
        return redirect("/")
    else:
        # Get list of symbols user owns
        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0",
                             session["user_id"])
        return render_template("sell.html", symbols=symbols)
