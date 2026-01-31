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

    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
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

    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO bosses (username, password, code) VALUES (?, ?, ?)",
                       (username, password, code))
        conn.commit()
        conn.close()
        return "Успешно зарегистрирован! Теперь войдите. <a href='/'>Войти</a>"
    except sqlite3.IntegrityError:
        conn.close()
        return "Такой пользователь уже есть! <a href='/'>Назад</a>"


@app.route('/index')
def index():
    if 'username' in session:

        conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, code FROM bosses WHERE username = ?", (session['username'],))
        users1 = cursor.fetchone()
        conn.close()

        if users1:
            username, code = users1


            conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
            cursor = conn.cursor()

            cursor.execute("SELECT name_task, task_description, data_issue_task FROM tasks")
            tasks = cursor.fetchall()
            conn.close()

            return render_template("index.html",username=username,code=code,tasks=tasks)
    return redirect(url_for('login_page'))


@app.route('/workers')
def workers():
    if 'username' not in session:
        return redirect(url_for('login_page'))

    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
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
    text = request.form.get('task_description')


    data_issue_task = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")





    if not name_task:
        return "Название задачи обязательно! <a href='/index'>Назад</a>"

    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET name_task = ?, task_description = ?, task_time = ?, check_acceptance = ?, degree_of_readiness = ?, data_issue_task = ? WHERE user_id = ?", ("делать проект",text,300,1,0,data_issue_task,427831749))
    conn.commit()
    conn.close()




    return redirect(url_for('index'))





@app.route('/out')
def logout():
    session.pop('username', None)
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)