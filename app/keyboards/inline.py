from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.database.db import list_directions, list_pzu_in_direction


def create_kb_for_contacts():
    "Создание клавиатуры для пункта меню /contacts"
    author_id = 897813157
    author_button = InlineKeyboardButton(
        text="Автор этого бота", url=f"tg://user?id={author_id}"
    )

    lomportbotchat_button = InlineKeyboardButton(
        text="Общий чат бота", url="https://t.me/lomportbotchat"
    )
    contacts_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[lomportbotchat_button], [author_button]]
    )
    return contacts_keyboard


def create_kb_for_help():
    lomport_url_button = InlineKeyboardButton(
        text="Будет время посетите мой сайт 🚛", url="https://lomovoz-portal.ru"
    )

    # Создаем объект инлайн-клавиатуры
    help_keyboard = InlineKeyboardMarkup(inline_keyboard=[[lomport_url_button]])
    return help_keyboard


# Создание клавиатуру для хендлера /list_pzu
async def create_kb_for_list_pzu() -> InlineKeyboardMarkup:
    request_result = await list_directions()
    request_result.sort()

    buttons = [
        InlineKeyboardButton(text=direction, callback_data=direction)
        for direction in request_result
    ]
    directions_keyboard = InlineKeyboardBuilder()
    directions_keyboard.row(*buttons, width=2)
    return directions_keyboard.as_markup()


# Создание клавиатуру для вывода пзу отдельного направления
async def create_kb_for_direction(direction: str) -> InlineKeyboardMarkup:
    request_result = await list_pzu_in_direction(direction)
    request_result.sort()
    buttons = [
        InlineKeyboardButton(text=pzu, callback_data=pzu) for pzu in request_result
    ]
    directions_keyboard = InlineKeyboardBuilder()
    if direction == "Заводы ЧМ":
        directions_keyboard.row(*buttons, width=2)
    else:
        directions_keyboard.row(*buttons, width=3)
    return directions_keyboard.as_markup()


# Инлайн-клавиатура с кнопками для выбора суммы доната
def donat_amount_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="100 руб", callback_data="amount_100"),
                InlineKeyboardButton(text="200 руб", callback_data="amount_200"),
            ],
            [
                InlineKeyboardButton(text="500 руб", callback_data="amount_500"),
                InlineKeyboardButton(text="1000 руб", callback_data="amount_1000"),
            ],
            [
                InlineKeyboardButton(
                    text="Другая сумма", callback_data="custom_amount"
                ),
            ],
        ]
    )


# Клавиатура для перехода к оплате
def transition_to_payment_keyboard(url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Перейти к оплате", url=url)]]
    )


# Объединение двух клавиатур в одну
combined_kb = create_kb_for_contacts()
# Добавляем кнопку "ПОДДЕРЖАТЬ"
combined_kb.inline_keyboard.insert(
    0, [InlineKeyboardButton(text="ПОДДЕРЖАТЬ", callback_data="/donate")]
)
