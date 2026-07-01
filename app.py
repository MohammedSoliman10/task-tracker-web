import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not any(char.isdigit() for char in password):
        return "Password must contain at least one number."
    if not any(char in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for char in password):
        return "Password must contain at least one special character."
    return None

app = Flask(__name__)
app.secret_key = "your_secret_key_123"

# ─── Flask-Login Setup ───
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ─── Database Setup ───
def get_db():
    db = sqlite3.connect("database.db")
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'todo',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    db.commit()
    db.close()

# ─── User Class ───
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    if user:
        return User(user["id"], user["username"])
    return None

# ─── Routes ───
@app.route("/")
@login_required
def index():
    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY id",
        (current_user.id,)
    ).fetchall()
    db.close()
    return render_template("index.html", tasks=tasks)

@app.route("/filter/<status>")
@login_required
def filter_tasks(status):
    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY id",
        (current_user.id, status)
    ).fetchall()
    db.close()
    return render_template("index.html", tasks=tasks, current_filter=status)

@app.route("/add", methods=["POST"])
@login_required
def add_task():
    description = request.form.get("description")
    if description:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "INSERT INTO tasks (description, status, created_at, updated_at, user_id) VALUES (?, ?, ?, ?, ?)",
            (description, "todo", now, now, current_user.id)
        )
        db.commit()
        db.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user.id))
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/mark-in-progress/<int:task_id>")
@login_required
def mark_in_progress(task_id):
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "UPDATE tasks SET status = 'in-progress', updated_at = ? WHERE id = ? AND user_id = ?",
        (now, task_id, current_user.id)
    )
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/mark-done/<int:task_id>")
@login_required
def mark_done(task_id):
    db = get_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "UPDATE tasks SET status = 'done', updated_at = ? WHERE id = ? AND user_id = ?",
        (now, task_id, current_user.id)
    )
    db.commit()
    db.close()
    return redirect(url_for("index"))

@app.route("/update/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    new_description = request.form.get("description")
    if new_description:
        db = get_db()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "UPDATE tasks SET description = ?, updated_at = ? WHERE id = ? AND user_id = ?",
            (new_description, now, task_id, current_user.id)
        )
        db.commit()
        db.close()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            error = validate_password(password)
            if error:
                flash(error, "error")
                return render_template("register.html")
            hashed_password = generate_password_hash(password)
            try:
                db = get_db()
                db.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hashed_password)
                )
                db.commit()
                db.close()
                flash("Account created! Please log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Email already exists. Try another one.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()
        if user and check_password_hash(user["password"], password):
            login_user(User(user["id"], user["username"]))
            return redirect(url_for("index"))
        flash("Wrong username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/admin")
@login_required
def admin():
    if current_user.username != "mohammedsolly4@gmail.com":
        flash("Access denied.", "error")
        return redirect(url_for("index"))
    db = get_db()
    users = db.execute("SELECT id, username FROM users").fetchall()
    tasks_count = db.execute("SELECT user_id, COUNT(*) as count FROM tasks GROUP BY user_id").fetchall()
    db.close()
    return render_template("admin.html", users=users, tasks_count=tasks_count)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)