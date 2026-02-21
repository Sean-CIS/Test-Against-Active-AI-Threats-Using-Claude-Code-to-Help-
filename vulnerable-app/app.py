"""
Intentionally Vulnerable Flask Application
==========================================
FOR SECURITY TESTING ONLY. DO NOT DEPLOY TO PRODUCTION.

This application contains deliberate security vulnerabilities for testing
AI-driven penetration testing tools like Strix. Each vulnerability is
labeled with its type for educational purposes.

Vulnerabilities included:
- SQL Injection (login, user lookup)
- Cross-Site Scripting / XSS (reflected, stored)
- Insecure Direct Object Reference / IDOR (invoice access)
- Command Injection (ping utility)
- Server-Side Request Forgery / SSRF (URL fetch)
- Broken Authentication (weak session handling)
- Path Traversal (file download)
- Missing Rate Limiting (login brute force)
"""

import os
import subprocess
import sqlite3
import hashlib
import secrets
import urllib.request
from functools import wraps
from flask import (
    Flask, request, jsonify, session, g, render_template_string,
    redirect, url_for, send_file
)

app = Flask(__name__)
app.secret_key = "hardcoded-secret-key-do-not-use"  # VULN: Hardcoded secret

DATABASE = "app.db"

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database with seed data."""
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        );
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed users (passwords stored as unsalted MD5 — intentionally weak)
    users = [
        ("admin", hashlib.md5(b"admin123").hexdigest(), "admin"),
        ("alice", hashlib.md5(b"password1").hexdigest(), "user"),
        ("bob", hashlib.md5(b"password2").hexdigest(), "user"),
    ]
    for username, password, role in users:
        try:
            db.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role),
            )
        except sqlite3.IntegrityError:
            pass

    # Seed invoices
    invoices = [
        (1, 5000.00, "Annual consulting fee"),
        (2, 1200.50, "Project Alpha payment"),
        (2, 750.00, "Project Beta deposit"),
        (3, 3200.00, "Infrastructure setup"),
        (3, 480.75, "Monthly maintenance"),
    ]
    for user_id, amount, desc in invoices:
        db.execute(
            "INSERT INTO invoices (user_id, amount, description) VALUES (?, ?, ?)",
            (user_id, amount, desc),
        )

    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return jsonify({
        "app": "Vulnerable Test Application",
        "warning": "FOR SECURITY TESTING ONLY",
        "endpoints": [
            "POST /api/login",
            "GET  /api/users/<username>",
            "GET  /api/invoices/<id>",
            "GET  /api/me",
            "POST /api/comments",
            "GET  /api/comments",
            "GET  /api/ping?host=<hostname>",
            "GET  /api/fetch?url=<url>",
            "GET  /api/download?file=<filename>",
            "GET  /api/search?q=<query>",
        ],
    })


# VULN: SQL Injection — string formatting in query
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")

    # VULNERABLE: String concatenation in SQL query
    password_hash = hashlib.md5(password.encode()).hexdigest()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password_hash}'"

    db = get_db()
    try:
        user = db.execute(query).fetchone()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        return jsonify({
            "message": "Login successful",
            "user": {"id": user["id"], "username": user["username"], "role": user["role"]},
        })

    return jsonify({"error": "Invalid credentials"}), 401


# VULN: SQL Injection — string formatting in user lookup
@app.route("/api/users/<username>")
def get_user(username):
    db = get_db()
    # VULNERABLE: String concatenation in SQL query
    query = f"SELECT id, username, role FROM users WHERE username = '{username}'"
    try:
        user = db.execute(query).fetchone()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if user:
        return jsonify(dict(user))
    return jsonify({"error": "User not found"}), 404


# VULN: IDOR — no authorization check, any logged-in user can access any invoice
@app.route("/api/invoices/<int:invoice_id>")
@login_required
def get_invoice(invoice_id):
    db = get_db()
    # VULNERABLE: No check that the invoice belongs to the logged-in user
    invoice = db.execute(
        "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
    ).fetchone()

    if invoice:
        return jsonify(dict(invoice))
    return jsonify({"error": "Invoice not found"}), 404


@app.route("/api/me")
@login_required
def me():
    return jsonify({
        "id": session["user_id"],
        "username": session["username"],
        "role": session["role"],
    })


# VULN: Stored XSS — comment content is not sanitized
@app.route("/api/comments", methods=["GET", "POST"])
def comments():
    db = get_db()

    if request.method == "POST":
        data = request.get_json(force=True)
        content = data.get("content", "")
        user_id = session.get("user_id")

        # VULNERABLE: No input sanitization — stored XSS
        db.execute(
            "INSERT INTO comments (user_id, content) VALUES (?, ?)",
            (user_id, content),
        )
        db.commit()
        return jsonify({"message": "Comment added"}), 201

    rows = db.execute("SELECT * FROM comments ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])


# VULN: Reflected XSS — search query echoed without escaping
@app.route("/api/search")
def search():
    query = request.args.get("q", "")
    # VULNERABLE: User input reflected directly in HTML response
    html = f"""
    <html>
    <body>
        <h1>Search Results</h1>
        <p>You searched for: {query}</p>
        <p>No results found.</p>
    </body>
    </html>
    """
    return render_template_string(html)


# VULN: Command Injection — user input passed to shell command
@app.route("/api/ping")
@login_required
def ping():
    host = request.args.get("host", "")
    if not host:
        return jsonify({"error": "Missing 'host' parameter"}), 400

    # VULNERABLE: Shell injection via unsanitized input
    try:
        result = subprocess.check_output(
            f"ping -c 1 {host}",
            shell=True,
            stderr=subprocess.STDOUT,
            timeout=5,
        )
        return jsonify({"output": result.decode()})
    except subprocess.CalledProcessError as e:
        return jsonify({"output": e.output.decode()}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"}), 504


# VULN: SSRF — server fetches arbitrary URLs
@app.route("/api/fetch")
@login_required
def fetch_url():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    # VULNERABLE: No URL validation — can reach internal services
    try:
        response = urllib.request.urlopen(url, timeout=5)
        content = response.read().decode("utf-8", errors="replace")
        return jsonify({"url": url, "status": response.status, "content": content[:5000]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# VULN: Path Traversal — no path sanitization on file download
@app.route("/api/download")
@login_required
def download():
    filename = request.args.get("file", "")
    if not filename:
        return jsonify({"error": "Missing 'file' parameter"}), 400

    # VULNERABLE: No path sanitization — can traverse directories
    filepath = os.path.join("uploads", filename)
    try:
        return send_file(filepath)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    # VULN: Debug mode enabled, binds to all interfaces
    app.run(host="0.0.0.0", port=5000, debug=True)
