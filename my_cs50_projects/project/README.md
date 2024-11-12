# EXPENSE TRACKER
#### Video Demo:  <URL https://youtu.be/p8JllOd38Fg>
https://youtu.be/p8JllOd38Fg
#### Description:
## Introduction

The **Expense Tracker** is a web-based application designed to help users monitor and manage their daily expenses. By allowing users to categorize, record, and review their spending, this tool aims to provide a clearer picture of personal finances, helping users make informed financial decisions. The application allows users to log their expenses, view a summary of their total spending, and access historical data in an organized format.

---

## Benefits

- **Financial Awareness**: The Expense Tracker empowers users by providing a clear view of where their money goes, enabling better budgeting and financial planning.
- **Simplicity and Accessibility**: With an intuitive design and straightforward interface, users can easily add expenses, view totals, and track spending without a steep learning curve.
- **Data Organization**: Users can categorize expenses, which makes it easy to identify spending patterns, track specific categories, and make adjustments to stay within budget.
- **Goal Achievement**: By tracking expenses, users can set savings goals and achieve financial stability, making this a valuable tool for anyone looking to improve their financial habits.

---

## How It Works

1. **User Registration and Login**: New users can register with a username and password, while existing users can log in to their account. This feature ensures that each user’s data remains private and secure.

2. **Adding Expenses**: Once logged in, users can add new expenses by specifying a category (like groceries, entertainment, etc.), amount, date, and description. Each expense is stored in the database, linked to the specific user.

3. **Viewing Total Expenses**: Users can view a summary of their total expenses on the home page. The application displays a breakdown of all expenses, organized by date and category, allowing users to analyze their spending at a glance.

4. **Expense History**: A history of all expenses is maintained, and users can access this data anytime to review past spending patterns, set new goals, or adjust budgets.

---

## How It is Built

The Expense Tracker is built using the **Flask** framework, a popular Python web framework known for its simplicity and flexibility. Here’s a breakdown of the major components:

- **Backend**: The backend of the application is developed in Python using Flask. Flask provides the routing for different pages (like login, registration, add expense, and view expenses) and manages session data to ensure secure login and personalized data access.

- **Database**: SQLite, a lightweight database, is used to store user data securely, including usernames, passwords (hashed for security), and expense entries. SQL commands are used to interact with the database for creating tables, inserting new expenses, and retrieving expense history.

- **Frontend**: The user interface is built using HTML and CSS, with a focus on creating a clean, responsive, and user-friendly design. Custom CSS styles ensure that the forms and tables are well-aligned, and visual elements like buttons and banners enhance the usability of the application.

- **Security**: Passwords are stored securely using hashing techniques, and user sessions are managed to ensure that each user’s data is kept private and secure.

- **Project Structure**: The project is divided into templates for HTML files, a `static` folder for CSS styles, and `app.py` as the main application file. This organized structure helps keep the code modular and easy to maintain.

---

## Summary

The Expense Tracker is a simple yet powerful tool to help users gain control over their finances. By combining a clean, accessible interface with essential features, this project provides an effective solution for personal financial management. Built with Flask, SQLite, and a well-designed frontend, this application demonstrates the utility and flexibility of web development technologies in addressing real-world problems.
TODO
