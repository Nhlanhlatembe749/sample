import sqlite3
from flask import Flask, render_template, request, g

app = Flask(__name__)
DB_PATH = 'messages.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO submissions (name, email, message) VALUES (?, ?, ?)",
                (name, email, message))
    conn.commit()

    print(f"Saved to DB: {name}, {email}, {message}")

    return f"""
    <h2>Thank you, {name}!</h2>
    <p>We received your message: <b>{message}</b></p>
    <a href="/">Go Back</a>
    """

@app.route('/submissions')
def submissions():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, message, created_at FROM submissions ORDER BY created_at DESC")
    rows = cur.fetchall()

    html = "<h1>Submissions</h1><a href='/'>Back</a><ul>"
    for r in rows:
        html += f"<li>[{r[0]}] <b>{r[1]}</b> ({r[2]}) at {r[4]}<br/>{r[3]}</li><hr>"
    html += "</ul>"
    return html

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
