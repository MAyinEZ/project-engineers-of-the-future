from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Посмотреть задание")],
            [KeyboardButton(text="🏆 Завершить задание")],
            [KeyboardButton(text="📝 Перерегистрация")]
        ],
        resize_keyboard=True
    )
    return keyboard

def inline():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅Принять", callback_data="yes"))
    builder.add(InlineKeyboardButton(text="❌Отказаться", callback_data="no"))
    builder.adjust(2)
    return builder.as_markup()

def inline2():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Да", callback_data="accept"))
    builder.add(InlineKeyboardButton(text="❌ Нет", callback_data="cancel"))
    builder.adjust(2)
    return builder.as_markup()

def cancel():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌Отмена", callback_data="cancel"))
    return builder.as_markup()

def degree_readiness_but():
    builder = InlineKeyboardBuilder()
    for number in range(1, 11):
        builder.button(text=f"{number}", callback_data=f"num_{number}")
    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup()