from aiogram import types, Router, Bot, F
from aiogram.fsm.state import State, StatesGroup
import keyboards
import sqlite3
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import os
from data import delete_message, waiting_for_file, datalastcall
from datetime import datetime
import math
from aiogram.types import CallbackQuery
from datetime import datetime

router = Router()

class UserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_patronymic = State()
    waiting_for_code = State()

class over_take(StatesGroup):
    waiting = State()

class refusal_task(StatesGroup):
    waiting_for_answer = State()

class del_user(StatesGroup):
    waiting_for_choose = State()

@router.callback_query(F.data == "yes")
async def accept(callback: CallbackQuery, bot:Bot):
    user_id = callback.from_user.id
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = users.cursor()
    cursor.execute("UPDATE tasks SET check_acceptance = ? WHERE user_id = ?", (2,user_id))
    cursor.execute("SELECT task_description, task_time, sent_message FROM tasks WHERE user_id = ?",(user_id,))
    user = cursor.fetchone()
    cursor.execute("UPDATE workers SET task_description = ?, task_time = ?, task_start_time = datetime('now', '+3 hours'), check_for_reminder = NULL WHERE user_id = ?", 
    (user[0],user[1],user_id))
    users.commit()
    users.close()
    await callback.message.answer("✅Задание принято!",reply_markup = keyboards.keyboard())
    await delete_message(bot, user_id, user[2])
@router.callback_query(F.data == "no")
async def accept(callback: CallbackQuery, state: FSMContext,bot:Bot):
    user_id = callback.from_user.id
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = users.cursor()
    cursor.execute("SELECT sent_message FROM tasks WHERE user_id = ?",(user_id,))
    user = cursor.fetchone()
    await delete_message(bot, user_id, user[0])
    cursor.execute("UPDATE tasks SET check_acceptance = ? WHERE user_id = ?", (5,user_id))
    users.commit()
    users.close()
    await callback.message.answer("Объясните причину отказа от задания:", reply_markup = keyboards.cancel())
    await state.set_state(refusal_task.waiting_for_answer)
@router.message(refusal_task.waiting_for_answer)
async def registration_name(message: types.Message, state: FSMContext, bot:Bot):
    answer = message.text
    await message.delete() 
    last_message_id = message.message_id
    user_id = message.from_user.id
    await delete_message(bot, user_id, last_message_id - 1)
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = users.cursor()
    cursor.execute("UPDATE tasks SET check_acceptance = ?, explanation_reason_refusal = ? WHERE user_id = ?", (3,answer,user_id))
    users.commit()
    users.close()
    await state.clear()
    await message.answer("❌Ваш отказ принят.")

@router.callback_query(F.data == "cancel")
async def cancel_state_handler(callback: types.CallbackQuery, state: FSMContext, bot:Bot):
    current_state = await state.get_state()
    user_id = callback.from_user.id
    if current_state == "refusal_task:waiting_for_answer":
        conn_users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
        cursor = conn_users.cursor()
        cursor.execute("SELECT task_description, task_time, sent_message FROM tasks WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        hour = math.floor(user[1]/ 3600)
        minute = math.floor((user[1] - (hour * 3600)) / 60)
        second = user[1] - (hour * 3600) - (minute * 60) 
        time = f"{hour}:{minute}:{second}"

        await delete_message(bot, user_id, user[2])   
        text = f"👋У вас новое задание📋\n\nВаше задание:\n{user[0]}\n\nДанное на него время: {time}"
        msg = await bot.send_message(user_id,text, reply_markup = keyboards.inline())
        await delete_message(bot, user_id, msg.message_id - 1) 
        cursor.execute("UPDATE tasks SET check_acceptance = ?, sent_message = ? WHERE user_id = ?", (1,msg.message_id,user_id))
        conn_users.commit()
        conn_users.close()
    elif current_state is None:
        await callback.message.answer("Нечего отменять.")
        return
    elif current_state == "over_take:waiting":
        msg = await callback.message.answer("Отмена выполнена.")
        waiting_for_file.remove(user_id)
        await delete_message(bot, user_id, msg.message_id - 1) 
    elif current_state == "del_user:waiting_for_choose":
        msg = await callback.message.answer("Отмена выполнена.")
        await delete_message(bot, user_id, msg.message_id - 1) 
    await state.clear()

@router.callback_query(F.data.startswith("num_"))
async def degree_readiness(callback: types.CallbackQuery,bot:Bot):
    number_str = callback.data.replace("num_", "")
    selected_number = int(number_str)
    user_id = callback.from_user.id
    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET degree_of_readiness = ? WHERE user_id = ?",(selected_number,user_id))
    conn.commit()
    conn.close()
    msg = await callback.message.answer(f"✅ Вы выбрали: {selected_number}",reply_markup=keyboards.keyboard())
    await delete_message(bot, user_id, msg.message_id - 1) 
        

@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM workers WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    await message.delete()
    
    if user_data:
        datalastcall(user_id)
        await message.answer(
            f"👋 С возвращением, {user_data[2]}!\n\n"
            "Вот что вы можете сделать:\n"
            "• 📋 Посмотреть порученное вам задание\n"
            "• 🏆 Завершить текущее задание\n"           #Данная часть кода срабатывает если пользователь уже зарегистрирован.
            "• 📝 Сделать перерегистрацию\n"
            "     (Если что-то ввели не так)\n\n"
            "Используйте кнопки ниже для навигации!",
            reply_markup=keyboards.keyboard()
        )
    else:
        await state.set_state(UserStates.waiting_for_name)
        await message.answer(
            "👋 Добро пожаловать! Давайте зарегистрируем вас в системе.\n\n"
            "Пожалуйста, введите ваше имя:"
        )
@router.message(UserStates.waiting_for_name)
async def registration_name(message: types.Message, state: FSMContext, bot:Bot):
    name = message.text.strip()
    await message.delete() 
    last_message_id = message.message_id
    user_id = message.from_user.id
    await delete_message(bot, user_id, last_message_id - 1)
    await state.update_data(name=name)
    await state.set_state(UserStates.waiting_for_surname)
    await message.answer("Теперь введите вашу фамилию:")
@router.message(UserStates.waiting_for_surname)
async def registration_surname(message: types.Message, state: FSMContext, bot:Bot):
    surname = message.text.strip()
    await message.delete() 
    last_message_id = message.message_id
    user_id = message.from_user.id
    await delete_message(bot, user_id, last_message_id - 1)
    await state.update_data(surname=surname)
    await state.set_state(UserStates.waiting_for_patronymic)
    await message.answer("Теперь введите ваше отчество:")
@router.message(UserStates.waiting_for_patronymic)
async def registration_patronymic(message: types.Message, state: FSMContext,bot:Bot):
    patronymic = message.text.strip()
    await message.delete() 
    last_message_id = message.message_id
    user_id = message.from_user.id
    await delete_message(bot, user_id, last_message_id - 1)
    await state.update_data(patronymic=patronymic)
    await state.set_state(UserStates.waiting_for_code)
    await message.answer("Отлично!\nТеперь напишите код данный вашим боссом/начальником:")
@router.message(UserStates.waiting_for_code)
async def registration_code(message: types.Message, state: FSMContext, bot:Bot):
    code = message.text
    await message.delete()
    last_message_id = message.message_id
    user_id = message.from_user.id
    await delete_message(bot, user_id, last_message_id - 1)
    conn = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bosses WHERE code = ?", (code,))
    user = cursor.fetchone()

    if user is None:
        await state.clear()
        conn.close()
        await message.answer("❌ Вашего кода не найдено.\n\nДля того чтобы заново начать регистрацию введите: /start")
    else:
        user_data = await state.get_data()
        name = user_data.get('name')
        surname = user_data.get('surname')
        patronymic = user_data.get('patronymic')
        username = message.from_user.username
        
        cursor.execute("INSERT INTO workers (user_id, username, name, surname, patronymic, code, data_last_call) VALUES (?, ?, ?, ?, ?, ?, datetime('now', '+3 hours'))",
        (user_id, username, name, surname, patronymic, code))
        cursor.execute("INSERT INTO tasks (user_id) VALUES (?)",(user_id,))
        cursor.execute("SELECT name, surname, patronymic FROM bosses WHERE code = ?", (code,))
        boss = cursor.fetchone()
        conn.commit()
        conn.close()
        
        await state.clear()
        
        os.makedirs(rf"C:\Users\provi\OneDrive\Desktop\project\папки пользователей\{user_id}", exist_ok=True)

        text = f"🎉 Регистрация завершена!\n\nВаши данные:\n👤 Имя: {name}\n👤 Фамилия: {surname}\n👤 Отчество: {patronymic}\n"
        f"💼 Ваш начальник: {boss[0]} {boss[1]} {boss[2]}\n\nТеперь вы можете использовать все возможности бота! Введите /start"
        await message.answer(text)

@router.message(lambda message: message.text == "📝 Перерегистрация")
async def delete_data_user(message: types.Message, state: FSMContext, bot:Bot):
    user_id = message.from_user.id
    await message.delete() 
    last_message_id = message.message_id
    await delete_message(bot, user_id, last_message_id - 1)
    await state.set_state(del_user.waiting_for_choose)
    await message.answer("Вы уверены?", reply_markup = keyboards.inline2())
@router.callback_query(F.data == "accept")
async def accept(callback: CallbackQuery, state: FSMContext, bot:Bot):
    user_id = callback.from_user.id
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor = users.cursor()
    cursor.execute("DELETE FROM workers WHERE user_id = ?",(user_id,))
    cursor.execute("DELETE FROM tasks WHERE user_id = ?",(user_id,))
    users.commit()
    users.close()
    await state.clear()
    msg = await callback.message.answer("✅Данные удалены! Введите /start для перерегистрации.",reply_markup = types.ReplyKeyboardRemove())
    await delete_message(bot, user_id, msg.message_id - 1) 

@router.message(lambda message: message.text == "📋 Посмотреть задание")
async def current_task(message: types.Message, bot:Bot):
    user_id = message.from_user.id
    datalastcall(user_id)
    await message.delete() 
    last_message_id = message.message_id
    await delete_message(bot, user_id, last_message_id - 1)
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor_users = users.cursor()
    cursor_users.execute("SELECT task_description, task_time, task_start_time FROM workers WHERE user_id = ?",(user_id,))
    user_data = cursor_users.fetchone()
    
    if user_data[0] is None:
        users.close()
        await message.answer("📭 У вас нет активных заданий.",reply_markup=keyboards.keyboard())
        return
    
    users.close()
    
    now = datetime.now()
    start = datetime.fromisoformat(user_data[2])
    time_passed = now - start
    time_remaining = user_data[1] - time_passed.seconds
    hour = math.floor(time_remaining / 3600)
    minute = math.floor((time_remaining - (hour * 3600)) / 60)
    second = time_remaining - (hour * 3600) - (minute * 60) 
    time = f"{hour}:{minute}:{second}"

    await message.answer(
        f"Ваше текущее задание:\n\n{user_data[0]}\n\nВаше оставшееся время: {time}",reply_markup=keyboards.keyboard()
    )

@router.message(lambda message: message.text == "🏆 Завершить задание")
async def complete_task(message: types.Message,state: FSMContext, bot:Bot):
    user_id = message.from_user.id
    datalastcall(user_id)
    waiting_for_file.add(user_id)
    await message.delete() 
    last_message_id = message.message_id
    await delete_message(bot, user_id, last_message_id - 1)
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor_users = users.cursor()
    cursor_users.execute("SELECT task_description FROM workers WHERE user_id = ?",(user_id,))
    user_data = cursor_users.fetchone()
    
    if user_data[0] is None:
        users.close()
        await message.answer("❌ У вас нет активных заданий для завершения.",reply_markup=keyboards.keyboard())
        return
    
    await state.set_state(over_take.waiting)
    await message.answer("Для завершения задания, отправьте файл, либо отправьте сообщение-отчёт о выполненном задании:", reply_markup = keyboards.cancel())
@router.message(over_take.waiting,lambda message: message.document or message.photo or message.text)
async def handle_files(message: types.Message, state: FSMContext, bot:Bot):
    user_id = message.from_user.id
    last_message_id = message.message_id
    await delete_message(bot, user_id, last_message_id - 1) 
    if message.document:
        file = message.document
        file_name = file.file_name
        file_id = file.file_id
        file_info = await bot.get_file(file_id)
        await bot.download_file(file_info.file_path, rf"C:\Users\provi\OneDrive\Desktop\project\папки пользователей\{user_id}\{file_name}")
        text = file_name
    elif message.photo:
        file = message.photo[-1]
        file_name = f"{file.file_name}.jpg"
        file_id = file.file_id
        file_info = await bot.get_file(file_id)
        await bot.download_file(file_info.file_path, rf"C:\Users\provi\OneDrive\Desktop\project\папки пользователей\{user_id}\{file_name}")
        text = file_name
    else:
        text = message.text

    await message.answer("✅ Файл/отчёт отправлен")
    
    users = sqlite3.connect(r'C:\Users\provi\OneDrive\Desktop\project\database\users.db')
    cursor_users = users.cursor()
    cursor_users.execute("SELECT task_description FROM workers WHERE user_id = ?",(user_id,))
    user_data = cursor_users.fetchone()
    await message.answer(f"🎉Поздравляем вы завершили задание:\n\n{user_data[0]}",reply_markup=keyboards.keyboard())
    cursor_users.execute("UPDATE workers SET task_description = NULL, task_time = NULL, task_start_time = NULL, check_for_reminder = NULL WHERE user_id = ?",(user_id,))
    cursor_users.execute("UPDATE tasks SET check_acceptance = ?, degree_of_readiness = ?, message_report = ? WHERE user_id = ?",(4,10,text,user_id))
    users.commit()
        
    await state.clear()
    waiting_for_file.remove(user_id)
    
    users.close()