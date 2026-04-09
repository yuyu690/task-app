import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATA_FILE = 'tasks.json'

# データ読み込み
def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# データ保存
def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# 初期化
tasks = load_tasks()

@app.route('/')
def home():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    task = request.form.get('task')
    deadline = request.form.get('deadline')
    subject = request.form.get('subject')
    if task and deadline and subject:
        tasks.append({'task': task, 'deadline': deadline, 'subject': subject})
        save_tasks(tasks)
    return redirect(url_for('home'))

@app.route('/delete', methods=['POST'])
def delete_task():
    index = int(request.form.get('index'))
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
