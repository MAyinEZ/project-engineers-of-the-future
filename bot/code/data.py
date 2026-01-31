import sqlite3
from aiogram.exceptions import TelegramBadRequest

waiting_for_file = set()

TOKEN = '7634566802:AAHCtstXjXwUc8DjM-Mdf9qrgnn7VXOlgMs'

def init_databases():
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor_users = users.cursor()
    cursor_users.execute('''CREATE TABLE IF NOT EXISTS workers (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        name TEXT,
        surname TEXT,
        patronymic TEXT,
        code TEXT,
        task_description TEXT,
        task_time INTEGER,
        task_start_time TIMESTAMP DEFAULT NULL,
        check_for_reminder INTEGER,
        sent_message INTEGER,
        data_last_call TIMESTAMP            
    )''')
    cursor_users.execute('''CREATE TABLE IF NOT EXISTS bosses (
        username TEXT,
        name TEXT,
        surname TEXT,
        patronymic TEXT,
        password TEXT,
        code TEXT
    )''')
    cursor_users.execute('''CREATE TABLE IF NOT EXISTS tasks (
        user_id INTEGER PRIMARY KEY,
        name_task TEXT DEFAULT NULL,
        task_description TEXT DEFAULT NULL,
        task_time INTEGER DEFAULT NULL,
        check_acceptance INTEGER DEFAULT NULL,
        sent_message INTEGER DEFAULT NULL,
        explanation_reason_refusal TEXT DEFAULT NULL,
        degree_of_readiness INTEGER DEFAULT NULL,
        message_report TEXT NULL,
        data_issue_task TIMESTAMP NULL
    )''')
    users.commit()
    users.close()

async def delete_message(bot, chat_id, message_id):
    if message_id is None:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        return
    except TelegramBadRequest as e:
        if "message can't be deleted" in str(e):
            return
        
def datalastcall(user_id):
    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE workers SET data_last_call = datetime('now', '+3 hours') WHERE user_id = ?",(user_id,))
    conn.commit()
    conn.close()
        
