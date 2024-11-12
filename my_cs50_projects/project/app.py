import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Initialize the Flask app
app = Flask(__name__)

# Configure application to use filesystem for session data
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
db = SQL("sqlite:///finance.db")

# Prevent caching of responses (helpful during development)
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Home route: displays the list of expenses
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    # Get all expenses for the current user
    expenses = db.execute("SELECT * FROM expenses WHERE user_id = ?", session["user_id"])

    # Calculate the total amount of expenses
    total_amount = db.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = ?", session["user_id"])[0]["total"]

    return render_template("index.html", expenses=expenses, total_amount=total_amount or 0)


# Register route: allows new users to sign up
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get the form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate form input
        if not username or not password or not confirmation:
            return "Please fill in all fields!"
        if password != confirmation:
            return "Passwords do not match!"

        # Hash the password for secure storage
        hash_password = generate_password_hash(password)

        # Insert the new user into the database
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_password)
        except:
            return "Username already exists."

        # Redirect the user to the login page
        flash("Registered successfully! Please log in.")
        return redirect("/login")

    # If GET request, render the registration page
    return render_template("register.html")

# Login route: allows users to log in
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        # Get the form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Retrieve the user from the database
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Verify username and password
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid username or password."

        # Remember the user's session
        session["user_id"] = rows[0]["id"]

        # Redirect to the home page
        return redirect("/")

    # If GET request, render the login page
    return render_template("login.html")

# Logout route: logs the user out
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# Add expense route: allows users to add a new expense
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        # Get form data
        category = request.form.get("category")
        amount = request.form.get("amount")
        date = request.form.get("date")
        description = request.form.get("description")

        # Validate form data
        if not category or not amount or not date:
            return "Please fill in all required fields."

        # Insert the expense into the database
        db.execute("INSERT INTO expenses (user_id, category, amount, date, description) VALUES (?, ?, ?, ?, ?)",
                   session["user_id"], category, float(amount), date, description)

        # Redirect to the home page
        return redirect("/")

    # If GET request, render the add expense page
    return render_template("add.html")
