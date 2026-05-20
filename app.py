from flask import Flask, request, redirect, session, url_for, render_template_string
import sqlite3
import bcrypt

app = Flask(__name__)
import os

app.secret_key = os.urandom(24)

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password BLOB
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Home
@app.route("/")
def home():
    if "user" in session:
        return f"Welcome {session['user']} <br><a href='/logout'>Logout</a>"
    return "<a href='/login'>Login</a> | <a href='/register'>Register</a>"

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            return redirect("/login")
        except:
            return "User already exists"

    return '''
    <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <button type="submit">Register</button>
    </form>
    '''

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cur = conn.cursor()

        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cur.fetchone()

        if result and bcrypt.checkpw(password.encode(), result[0]):
            session["user"] = username
            return redirect("/")
        else:
            return "Invalid credentials"

    return '''
    <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <button type="submit">Login</button>
    </form>
    '''

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# Run
if __name__ == "__main__":
    app.run(debug=True)