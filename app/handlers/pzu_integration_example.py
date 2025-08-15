"""
Пример интеграции проверки весового контроля в существующие хендлеры ПЗУ
Это показывает как модифицировать существующий код для добавления функционала
"""

from aiogram.types import Message
from aiogram import Router

# Импорты для работы с весовым контролем
from app.handlers.weight_control_handlers import add_weight_control_check_to_pzu_response

import logging

logger = logging.getLogger("lomportbot.pzu_integration")

router = Router()


# ПРИМЕР 1: Модификация существующего хендлера ПЗУ
async def handle_pzu_request_with_weight_control(message: Message, pzu_data: dict):
    """
    Пример обработки запроса ПЗУ с проверкой весового контроля
    
    Это показывает как модифицировать существующие хендлеры
    """
    
    # ===== СУЩЕСТВУЮЩАЯ ЛОГИКА БОТА =====
    # Здесь был бы ваш обычный код для обработки ПЗУ
    original_pzu_text = f"""
📍 ПЗУ: {pzu_data.get('name', 'Неизвестно')}
🗺️ Регион: {pzu_data.get('region', 'Не указан')}
📧 Контакты: {pzu_data.get('contacts', 'Не указаны')}
🕒 Режим работы: {pzu_data.get('working_hours', 'Не указан')}
"""
    
    # ===== НОВЫЙ ФУНКЦИОНАЛ: ПРОВЕРКА ВЕСОВОГО КОНТРОЛЯ =====
    try:
        # Добавляем проверку весового контроля
        updated_text, weight_control_keyboard = await add_weight_control_check_to_pzu_response(
            pzu_data, original_pzu_text
        )
        
        # Отправляем ответ с проверкой весового контроля
        if weight_control_keyboard:
            # Есть пункты весового контроля рядом - отправляем с предупреждением и кнопками
            await message.answer(
                updated_text,
                reply_markup=weight_control_keyboard,
                parse_mode="Markdown"
            )
        else:
            # Весового контроля рядом нет - отправляем обычный ответ
            await message.answer(original_pzu_text)
            
    except Exception as e:
        logger.error(f"Ошибка при проверке весового контроля: {e}")
        # В случае ошибки отправляем обычный ответ без проверки
        await message.answer(original_pzu_text)


# ПРИМЕР 2: Простая модификация существующего хендлера
"""
В вашем существующем файле app/handlers/commands.py можно добавить:

# В начало файла добавить импорт:
from app.handlers.weight_control_handlers import add_weight_control_check_to_pzu_response

# В функцию обработки ПЗУ (например, в районе строки где формируется ответ) добавить:

# ДО (существующий код):
await message.answer(pzu_response_text, reply_markup=existing_keyboard)

# ПОСЛЕ (с проверкой весового контроля):
if pzu_data.get('latitude') and pzu_data.get('longitude'):
    # Проверяем весовой контроль
    updated_text, weight_keyboard = await add_weight_control_check_to_pzu_response(
        pzu_data, pzu_response_text
    )
    
    if weight_keyboard:
        # Есть весовой контроль - отправляем с предупреждением
        await message.answer(updated_text, reply_markup=weight_keyboard, parse_mode="Markdown")
    else:
        # Нет весового контроля - обычный ответ
        await message.answer(pzu_response_text, reply_markup=existing_keyboard)
else:
    # Нет координат ПЗУ - обычный ответ
    await message.answer(pzu_response_text, reply_markup=existing_keyboard)
"""


# ПРИМЕР 3: Создание middleware для автоматической проверки
class WeightControlMiddleware:
    """
    Middleware для автоматической проверки весового контроля
    Может быть применен ко всем хендлерам ПЗУ
    """
    
    async def __call__(self, handler, event, data):
        # Выполняем основной хендлер
        result = await handler(event, data)
        
        # Если в данных есть информация о ПЗУ с координатами
        pzu_data = data.get('pzu_data')
        if pzu_data and pzu_data.get('latitude') and pzu_data.get('longitude'):
            # Можно добавить автоматическую проверку весового контроля
            pass
        
        return result


# ПРИМЕР 4: Функция для добавления в существующий роутер
def register_weight_control_handlers(router: Router):
    """
    Функция для регистрации хендлеров весового контроля в существующем роутере
    
    Добавьте эту строку в ваш главный файл с роутерами:
    register_weight_control_handlers(your_router)
    """
    from app.handlers.weight_control_handlers import router as weight_control_router
    
    # Включаем роутер весового контроля
    router.include_router(weight_control_router)


# ПРИМЕР 5: Утилита для быстрой проверки координат
async def quick_weight_control_check(lat: float, lon: float, name: str = "точка") -> str:
    """
    Быстрая проверка весового контроля для любых координат
    Возвращает строку с результатом для отправки пользователю
    """
    from app.services.weight_control_service import WeightControlService
    from app.utils.map_utils import generate_weight_control_warning
    
    try:
        weight_controls = await WeightControlService.find_nearby_weight_control(
            lat, lon, radius_km=50
        )
        
        if weight_controls:
            warning = generate_weight_control_warning(weight_controls)
            return f"⚠️ Предупреждение для {name}:\n\n{warning}"
        else:
            return f"✅ Рядом с {name} пунктов весового контроля не обнаружено"
            
    except Exception as e:
        logger.error(f"Ошибка при быстрой проверке: {e}")
        return f"❌ Ошибка при проверке весового контроля для {name}"
