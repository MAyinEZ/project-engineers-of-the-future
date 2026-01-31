import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

async def delete_users():
    conn_users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn_users.cursor()
    cursor.execute("SELECT data_last_call, user_id FROM workers")
    users = cursor.fetchall()
    now = datetime.now()
    for data_last_call, user_id in users:
        start = datetime.fromisoformat(data_last_call)
        time_passed = now - start
        if time_passed.days > 365:
            cursor.execute("DELETE FROM workers WHERE user_id = ?",(user_id,))
            cursor.execute("DELETE FROM tasks WHERE user_id = ?",(user_id,))
            conn_users.commit()

    conn_users.close()

scheduler_du = AsyncIOScheduler()
scheduler_du.add_job(
    delete_users,
    trigger=IntervalTrigger(days=1)
)