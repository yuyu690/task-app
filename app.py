from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret-key'  # 後で変える

DB_NAME = 'tasks.db'

# Flask-Login設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# DB接続
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ユーザークラス
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# 初期化
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            deadline TEXT,
            subject TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ホーム（ログイン必須）
@app.route('/')
@login_required
def home():
    conn = get_db()
    tasks = conn.execute(
        'SELECT * FROM tasks WHERE user_id = ?',
        (current_user.id,)
    ).fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# 登録
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))

        try:
            conn = get_db()
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

        except Exception as e:
            return f"エラー: {e}"

    return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))

        conn = get_db()
        conn.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, password)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html')

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            login_user(User(user['id']))
            return redirect(url_for('home'))

    return render_template('login.html')

# ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# タスク追加
@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task = request.form.get('task')
    deadline = request.form.get('deadline')
    subject = request.form.get('subject')

    conn = get_db()
    conn.execute(
        'INSERT INTO tasks (user_id, task, deadline, subject) VALUES (?, ?, ?, ?)',
        (current_user.id, task, deadline, subject)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

# 削除
@app.route('/delete', methods=['POST'])
@login_required
def delete_task():
    task_id = request.form.get('id')

    conn = get_db()
    conn.execute(
        'DELETE FROM tasks WHERE id = ? AND user_id = ?',
        (task_id, current_user.id)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

if __name__ == "__main__":
    init_db()
    app.run()
