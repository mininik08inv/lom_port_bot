from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict

from app.database.db import list_directions, list_pzu_in_direction
from app.utils.map_utils import generate_yandex_map_link


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


def create_weight_control_keyboard(weight_controls: List[Dict], search_lat: float = None, search_lon: float = None, search_radius: int = 50) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со ссылками на карты пунктов весового контроля
    
    Args:
        weight_controls: Список пунктов весового контроля с координатами
        search_lat: Широта центра поиска (для кнопки "Еще пункты")
        search_lon: Долгота центра поиска (для кнопки "Еще пункты")  
        search_radius: Радиус поиска в км (для кнопки "Еще пункты")
        
    Returns:
        InlineKeyboardMarkup с кнопками ссылок на карты
    """
    buttons = []
    
    # Ограничиваем количество кнопок для удобства
    limited_controls = weight_controls[:5]
    
    for wc in limited_controls:
        if wc.get('latitude') and wc.get('longitude'):
            distance = round(wc['distance'], 1)
            
            # Формируем текст кнопки с названием и расстоянием
            button_text = f"📍 {wc['name'][:25]}... ({distance} км)"
            
            # Создаем ссылку на Яндекс.Карты
            # map_link = generate_yandex_map_link(
            #     wc['latitude'],
            #     wc['longitude'],
            #     wc['name']
            # )

            map_link = wc['url']
            
            # Добавляем кнопку
            buttons.append([
                InlineKeyboardButton(
                    text=button_text,
                    url=map_link
                )
            ])
    
    # Если пунктов больше 5, добавляем кнопку для показа всех
    if len(weight_controls) > 5:
        # remaining_count = len(weight_controls) - 5
        
        # Формируем callback_data с координатами (сжато)
        if search_lat is not None and search_lon is not None:
            # Округляем координаты до 4 знаков для экономии места
            lat_short = round(search_lat, 4)
            lon_short = round(search_lon, 4)
            callback_data = f"wc_more:{lat_short}:{lon_short}:{search_radius}"
        else:
            callback_data = "weight_control_more_info"
        
        buttons.append([
            InlineKeyboardButton(
                text=f"📋 Показать все {len(weight_controls)} пунктов",
                callback_data=callback_data
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Объединение двух клавиатур в одну
combined_kb = create_kb_for_contacts()
# Добавляем кнопку "ПОДДЕРЖАТЬ"
combined_kb.inline_keyboard.insert(
    0, [InlineKeyboardButton(text="ПОДДЕРЖАТЬ", callback_data="/donate")]
)
