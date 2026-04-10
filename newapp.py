import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = 'tasks.db'

# DB接続
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# 初期化（テーブル作成）
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            deadline TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ホーム
@app.route('/')
def home():
    conn = get_db()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# 追加
@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    deadline = request.form.get('deadline')
    subject = request.form.get('subject')

    if task and deadline and subject:
        conn = get_db()
        conn.execute(
            'INSERT INTO tasks (task, deadline, subject) VALUES (?, ?, ?)',
            (task, deadline, subject)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('home'))

# 削除
@app.route('/delete', methods=['POST'])
def delete_task():
    task_id = request.form.get('id')

    conn = get_db()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

if __name__ == "__main__":
    init_db()
    app.run()