from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

with sqlite3.connect("users.db") as conn:
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        balance REAL DEFAULT 0
    )
    """)
    conn.commit()


@app.route("/")
def home():
    return render_template("bank.html", pagetitle="Khaled Bank")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

    if user:
        return redirect(f"/enter?username={username}")
    else:
        return "Username or password incorrect. <a href='/'>Go back</a>"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        except sqlite3.IntegrityError:
            return "Username already exists. <a href='/register'>Try again</a>"

        return redirect("/")

    return render_template("register.html")

@app.route("/enter")
def enter():
    username = request.args.get("username")
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE username=?", (username,))
        balance = cursor.fetchone()[0]
    return render_template("enter.html", username=username, balance=balance, pagetitle="Dashboard | Khaled Bank")


@app.route("/deposit", methods=["POST"])
def deposit():
    username = request.form.get("username")
    amount = float(request.form["amount"])
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE username=?", (amount, username))
    return redirect(f"/enter?username={username}")


@app.route("/withdraw", methods=["POST"])
def withdraw():
    username = request.form.get("username")
    amount = float(request.form["amount"])
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE username=?", (username,))
        balance = cursor.fetchone()[0]
        if amount > balance:
            return f"Not enough balance! <a href='/enter?username={username}'>Go back</a>"
        cursor.execute("UPDATE users SET balance = balance - ? WHERE username=?", (amount, username))
    return redirect(f"/enter?username={username}")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
