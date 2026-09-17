"""
Vulnerable Web Application - Baseline Version
Intentionally contains 4 security vulnerabilities for educational purposes.
DO NOT USE IN PRODUCTION.
"""

from flask import Flask, request, render_template_string
import os
import sqlite3

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')


def get_db():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize the database with a default admin user."""
    conn = get_db()
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER, username TEXT, password TEXT)')
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'password123')")
    conn.commit()
    conn.close()


@app.route('/')
def index():
    """Landing page listing all vulnerable endpoints."""
    return '''
    <h1>🔓 Vulnerable Web App</h1>
    <ul>
        <li><a href="/upload">📁 File Upload</a></li>
        <li><a href="/ping">💻 OS Command Injection</a></li>
        <li><a href="/search">🔍 XSS</a></li>
        <li><a href="/login">🔐 SQL Injection</a></li>
    </ul>
    '''


# =============================================================================
# VULNERABILITY 1: Unrestricted File Upload
# No file type, extension, or MIME validation is performed.
# An attacker can upload PHP webshells and achieve RCE.
# =============================================================================
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        # VULNERABLE: Uses original filename without sanitization or validation
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return f"<h2>✅ File uploaded to: {filepath}</h2><br><a href='/'>Back</a>"
    return '''
    <h2>📁 Upload File</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file"><br><br>
        <input type="submit" value="Upload">
    </form>
    <br><a href='/'>Back</a>
    '''


# =============================================================================
# VULNERABILITY 2: OS Command Injection
# User input is concatenated directly into a shell command via os.popen().
# Shell metacharacters ( ; | && ` ) allow arbitrary command execution.
# =============================================================================
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        host = request.form['host']
        # VULNERABLE: Direct string interpolation into shell command
        result = os.popen(f"ping -c 1 {host}").read()
        return f"<h2>Ping Result</h2><pre>{result}</pre><br><a href='/'>Back</a>"
    return '''
    <h2>💻 Ping Tool</h2>
    <form method="post">
        Host: <input type="text" name="host" placeholder="8.8.8.8"><br><br>
        <input type="submit" value="Ping">
    </form>
    <br><a href='/'>Back</a>
    '''


# =============================================================================
# VULNERABILITY 3: Reflected Cross-Site Scripting (XSS)
# User input is reflected directly into HTML without encoding or escaping.
# Payloads like <script>alert(1)</script> execute in the victim's browser.
# =============================================================================
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # VULNERABLE: Raw user input rendered directly in HTML response
    return f'''
    <h2>🔍 Search</h2>
    <form>
        <input type="text" name="q" value="{query}">
        <input type="submit" value="Search">
    </form>
    <p>Results for: {query}</p>
    <br><a href='/'>Back</a>
    '''


# =============================================================================
# VULNERABILITY 4: SQL Injection
# SQL query is built via string concatenation with user-supplied input.
# Authentication bypass possible with: admin' OR '1'='1' --
# =============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        # VULNERABLE: Dynamic SQL string concatenation
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        user = cursor.fetchone()
        if user:
            return f"<h2>✅ Welcome, {username}!</h2><br><a href='/'>Back</a>"
        return "<h2>❌ Invalid credentials</h2><br><a href='/login'>Try Again</a>"
    return '''
    <h2>🔐 Login</h2>
    <form method="post">
        Username: <input type="text" name="username"><br><br>
        Password: <input type="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
    <br><a href='/'>Back</a>
    '''


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)