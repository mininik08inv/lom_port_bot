from aiogram.types import message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Создаем клавиатуру для отмены
def get_cancel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
