from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.db import get_db_connection, execute_query, list_directions, list_pzu_in_direction

# Создаем объекты инлайн-кнопок
author_id = 897813157
author_button = InlineKeyboardButton(
    text='Автор этого бота',
    url=f'tg://user?id={author_id}'
)

lomportbotchat_button = InlineKeyboardButton(
    text='Общий чат бота',
    url='https://t.me/lomportbotchat'
)

lomport_url_button = InlineKeyboardButton(
    text='Будет время посетите мой сайт 🚛',
    url='https://lomovoz-portal.ru'
)

# Создаем объект инлайн-клавиатуры
help_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[lomport_url_button]]
)

contacts_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[lomportbotchat_button],
                     [author_button]]
)

# Создание клавиатуру для хендлера /list_pzu
def create_kb_for_list_pzu():
    request_result = list_directions()
    request_result.sort()
    result_data = [i[0] for i in request_result]

    buttons = [InlineKeyboardButton(text=direction, callback_data=direction) for direction in result_data]
    directions_keyboard = InlineKeyboardBuilder()
    directions_keyboard.row(*buttons, width=2)
    return directions_keyboard


# Создание клавиатуру для вывода пзу отдельного направления
def create_kb_for_direction(direction):
    request_result = list_pzu_in_direction(direction)
    request_result.sort()
    buttons = [InlineKeyboardButton(text=pzu, callback_data=pzu) for pzu in request_result]
    directions_keyboard = InlineKeyboardBuilder()
    if direction == 'Заводы ЧМ':
        directions_keyboard.row(*buttons, width=2)
    else:
        directions_keyboard.row(*buttons, width=3)
    return directions_keyboard
