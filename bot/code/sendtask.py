import sqlite3
from aiogram import Bot
from data import TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import math
from data import delete_message
import keyboards

bot = Bot(token=TOKEN)

async def send_task():
    conn_users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn_users.cursor()
    cursor.execute("SELECT user_id, name_task, task_description, task_time, sent_message FROM tasks WHERE check_acceptance = 1")
    users = cursor.fetchall()
    for user_id, name_task, task_description, task_time, sent_message in users:
        hour = math.floor(task_time / 3600)
        minute = math.floor((task_time - (hour * 3600)) / 60)
        second = task_time - (hour * 3600) - (minute * 60) 
        time = f"{hour}:{minute}:{second}"

        cursor.execute("UPDATE workers SET task_description = NULL, task_time = NULL, task_start_time = NULL, check_for_reminder = NULL WHERE user_id = ?",(user_id,))
        await delete_message(bot, user_id, sent_message)   
        text = f"👋У вас новое задание📋\n\nВаше задание:\n{name_task}\n\nОписание:\n{task_description}\n\nДанное на него время: {time}"
        msg = await bot.send_message(user_id,text, reply_markup = keyboards.inline())
        await delete_message(bot, user_id, msg.message_id - 1) 
        cursor.execute("UPDATE tasks SET sent_message = ? WHERE user_id = ?", (msg.message_id,user_id))
        conn_users.commit()

    conn_users.close()

scheduler_st = AsyncIOScheduler()
scheduler_st.add_job(
    send_task,
    trigger=IntervalTrigger(minutes=1)
)