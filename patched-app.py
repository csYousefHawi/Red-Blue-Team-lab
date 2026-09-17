"""
Secure Web Application - Patched Version
All 4 vulnerabilities from the baseline have been remediated.
"""

from flask import Flask, request, render_template_string
from markupsafe import escape
import os
import sqlite3
import subprocess
import re

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')

# Whitelist of allowed file extensions for upload validation
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


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


def allowed_file(filename):
    """
    Validate uploaded file against an extension whitelist.
    Returns True only if the extension is in ALLOWED_EXTENSIONS.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Landing page for the patched application."""
    return '''
    <h1>🔒 Secure Web App (Patched)</h1>
    <p>This app is fixed — vulnerabilities have been patched.</p>
    <ul>
        <li><a href="/upload">📁 File Upload</a></li>
        <li><a href="/ping">💻 Ping Tool</a></li>
        <li><a href="/search">🔍 Search</a></li>
        <li><a href="/login">🔐 Login</a></li>
    </ul>
    '''


# =============================================================================
# FIX 1: File Upload — Extension whitelist + filename sanitization
# =============================================================================
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # Sanitize filename to prevent directory traversal
            safe_filename = os.path.basename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
            file.save(filepath)
            return f"<h2>✅ File uploaded: {escape(safe_filename)}</h2><br><a href='/'>Back</a>"
        else:
            return "<h2>❌ Invalid file type. Only images and PDF allowed.</h2><br><a href='/upload'>Try Again</a>"
    return '''
    <h2>📁 Upload File</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file"><br><br>
        <input type="submit" value="Upload">
    </form>
    <br><a href='/'>Back</a>
    '''


# =============================================================================
# FIX 2: OS Command Injection — Input validation + subprocess with list
# =============================================================================
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        host = request.form['host']
        # Validate: allow only alphanumeric, dots, and dashes (IP or hostname)
        if not re.match(r'^[a-zA-Z0-9\.\-]+$', host):
            return "<h2>❌ Invalid host format</h2><br><a href='/ping'>Try Again</a>"
        try:
            # SECURE: subprocess.run() with a list prevents shell injection
            result = subprocess.run(
                ['ping', '-c', '1', host],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = escape(result.stdout + result.stderr)
            return f"<h2>Ping Result</h2><pre>{output}</pre><br><a href='/'>Back</a>"
        except Exception as e:
            return f"<h2>Error: {escape(str(e))}</h2><br><a href='/ping'>Try Again</a>"
    return '''
    <h2>💻 Ping Tool</h2>
    <form method="post">
        Host: <input type="text" name="host" placeholder="8.8.8.8"><br><br>
        <input type="submit" value="Ping">
    </form>
    <br><a href='/'>Back</a>
    '''


# =============================================================================
# FIX 3: XSS — All user output passed through markupsafe.escape()
# =============================================================================
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # SECURE: Escape special HTML characters (< > " ' &) before rendering
    safe_query = escape(query)
    return f'''
    <h2>🔍 Search</h2>
    <form>
        <input type="text" name="q" value="{safe_query}">
        <input type="submit" value="Search">
    </form>
    <p>Results for: {safe_query}</p>
    <br><a href='/'>Back</a>
    '''


# =============================================================================
# FIX 4: SQL Injection — Parameterized queries with SQLite placeholders
# =============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        # SECURE: User input is bound as data, not executable SQL
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()
        if user:
            safe_username = escape(username)
            return f"<h2>✅ Welcome, {safe_username}!</h2><br><a href='/'>Back</a>"
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