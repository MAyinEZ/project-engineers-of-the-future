import sqlite3
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from data import TOKEN, waiting_for_file, delete_message
from datetime import datetime
import math
import keyboards

bot = Bot(token=TOKEN)

async def reminder():
    conn_users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn_users.cursor()
    cursor.execute("SELECT user_id, task_description, task_time, task_start_time, check_for_reminder, sent_message FROM workers WHERE task_description IS NOT NULL")
    users = cursor.fetchall()
    now = datetime.now()
    for user_id, task_description, task_time, task_start_time, check_for_reminder, sent_message in users:
        start = datetime.fromisoformat(task_start_time)
        time_passed = now - start
        time_remaining = task_time - time_passed.seconds

        if time_remaining > 0:
            hour = math.floor(time_remaining / 3600)
            minute = math.floor((time_remaining - (hour * 3600)) / 60)
            second = time_remaining - (hour * 3600) - (minute * 60) 

            time = f"{hour}:{minute}:{second}"

            if task_time / 3 <= time_passed.seconds and check_for_reminder is None and user_id not in waiting_for_file:
                await delete_message(bot, user_id, sent_message)   
                text = f"Напоминаем.\n\nВаше задание:\n{task_description}\n\nВаше оставшееся время: {time} \n\nОцените степень готовности:"
                msg= await bot.send_message(user_id,text,reply_markup=keyboards.degree_readiness_but())
                await delete_message(bot, user_id, msg.message_id - 1) 
                cursor.execute("UPDATE workers SET check_for_reminder = ?, sent_message = ? WHERE user_id = ?", (1,msg.message_id,user_id))
                conn_users.commit()
            elif task_time * 2 / 3 <= time_passed.seconds and check_for_reminder == 1 and user_id not in waiting_for_file:
                await delete_message(bot, user_id, sent_message)   
                text = f"Напоминаем.\n\nВаше задание:\n{task_description}\n\nВаше оставшееся время: {time}\n\nОцените степень готовности:"
                msg= await bot.send_message(user_id,text,reply_markup=keyboards.degree_readiness_but())
                await delete_message(bot, user_id, msg.message_id - 1) 
                cursor.execute("UPDATE workers SET check_for_reminder = ?, sent_message = ? WHERE user_id = ?", (2,msg.message_id,user_id))
                conn_users.commit()
        elif time_remaining < 0 and user_id not in waiting_for_file:
            await delete_message(bot, user_id, sent_message)   
            text = f"Ваше время вышло.\n\nВаше задание:\n{task_description}\n\nЗадание автоматически завершено."
            msg = await bot.send_message(user_id,text,reply_markup=keyboards.keyboard())
            await delete_message(bot, user_id, msg.message_id - 1)  
            text1 = "❌Задание невыполнено вовремя." 
            cursor.execute("UPDATE workers SET task_description = NULL, task_time = NULL, task_start_time = NULL, check_for_reminder = NULL WHERE user_id = ?",(user_id,))
            cursor.execute("UPDATE tasks SET check_acceptance = ?, explanation_reason_refusal = ? WHERE user_id = ?", (3,text1,user_id))
            conn_users.commit()

    conn_users.close()

scheduler_rem = AsyncIOScheduler()
scheduler_rem.add_job(
    reminder,
    trigger=IntervalTrigger(minutes=1)
)
