from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime


app = Flask(__name__)
app.secret_key = 'Sasha_key'





@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('user')
    password = request.form.get('pwd')

    if not username or not password:
        return "Заполните все поля! <a href='/'>Назад</a>"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM bosses WHERE username = ?", (username,))
    res = cursor.fetchone()
    conn.close()

    if res:
        if res[0] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Пароль неверный! <a href='/'>Назад</a>"
    else:
        return "Такого пользователя нет! <a href='/'>Назад</a>"


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('user')
    password = request.form.get('pwd')
    code = request.form.get('code')

    if not username or not password or not code:
        return "Заполните все поля! <a href='/'>Назад</a>"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM bosses WHERE username = ?", (username,))
    notuser = cursor.fetchone()

    if notuser:
        conn.close()
        return "Такой пользователь уже существует! <a href='/'>Назад</a>"


    cursor.execute("SELECT code FROM bosses WHERE code = ?", (code,))
    notcode = cursor.fetchone()

    if notcode:
        conn.close()
        return "Такой код уже существует! <a href='/'>Назад</a>"

    try:
        cursor.execute(
            "INSERT INTO bosses (username, password, code) VALUES (?, ?, ?)",
            (username, password, code)
        )
        conn.commit()
        conn.close()
        return "Успешно зарегистрирован! <a href='/'>Войти</a>"

    except sqlite3.IntegrityError:
        conn.close()
        return "Такой пользователь уже есть! <a href='/'>Назад</a>"


@app.route('/index')
def index():
    if 'username' in session:

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute("SELECT username, code FROM bosses WHERE username = ?", (session['username'],))
        user_data = cursor.fetchone()

        cursor.execute("SELECT name_task, task_description, data_issue_task FROM tasks")
        tasks = cursor.fetchall()

        cursor.execute("SELECT username, name, surname, patronymic, code, task_description FROM workers")
        workers = cursor.fetchall()

        conn.close()

        if user_data:
            username, code = user_data
            return render_template("index.html", username=username, code=code, tasks=tasks, workers=workers)

    return redirect(url_for('login_page'))
@app.route('/workers')
def workers():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()


    cursor.execute("SELECT username, name, surname, patronymic, code, task_description FROM workers")
    workers_list = cursor.fetchall()
    conn.close()

    return render_template('workers.html',username=session['username'],workers=workers_list)

@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    name_task = request.form.get('name_task')
    worker_username = request.form.get('worker_username')
    days = request.form.get('days')

    if not name_task or not worker_username or not days:
        return "Заполните все поля! <a href='/index'>Назад</a>"

    try:
        days = int(days)
    except:
        return "Срок должен быть числом! <a href='/index'>Назад</a>"


    task_text = f"{name_task} ({days} дней)"

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()


    cursor.execute("SELECT task_description FROM workers WHERE username = ?", (worker_username,))
    cur = cursor.fetchone()

    if cur and cur[0]:
        conn.close()
        return "У рабочего уже есть задача, подождите выполнения! <a href='/index'>Назад</a>"

    cursor.execute("""
        UPDATE workers
        SET task_description = ?
        WHERE username = ?
    """, (task_text, worker_username))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))
@app.route('/out')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)