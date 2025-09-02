"""
Обработчики для интеграции весового контроля с ПЗУ
"""

from typing import Tuple, Optional, Dict, Any
from aiogram.types import InlineKeyboardMarkup
from aiogram import Router

from app.services.weight_control_service import WeightControlService
from app.utils.map_utils import generate_weight_control_warning
from app.keyboards.inline import create_weight_control_keyboard

import logging

logger = logging.getLogger("lomportbot.weight_control_handlers")

router = Router()


async def add_weight_control_check_to_pzu_response(
    pzu_data: Dict[str, Any], 
    original_message: str
) -> Tuple[str, Optional[InlineKeyboardMarkup]]:
    """
    Добавляет проверку весового контроля к ответу о ПЗУ
    
    Args:
        pzu_data: Словарь с данными ПЗУ, должен содержать 'latitude' и 'longitude'
        original_message: Оригинальное сообщение о ПЗУ
        
    Returns:
        Кортеж (обновленное_сообщение, клавиатура_или_None)
    """
    try:
        # Проверяем наличие координат
        if not pzu_data.get('latitude') or not pzu_data.get('longitude'):
            logger.warning(f"ПЗУ {pzu_data.get('name', 'unknown')} не имеет координат для проверки весового контроля")
            return original_message, None
        
        lat = float(pzu_data['latitude'])
        lon = float(pzu_data['longitude'])
        
        logger.info(f"🔍 Проверяем весовой контроль для ПЗУ {pzu_data.get('name', 'unknown')} "
                   f"на координатах {lat}, {lon}")
        
        # Ищем ближайшие пункты весового контроля
        weight_controls = await WeightControlService.find_nearby_weight_control(
            lat, lon, radius_km=50
        )
        
        if not weight_controls:
            logger.info(f"✅ Пунктов весового контроля рядом с ПЗУ {pzu_data.get('name', 'unknown')} не найдено")
            return original_message, None
        
        logger.info(f"⚠️ Найдено {len(weight_controls)} пунктов весового контроля рядом с ПЗУ {pzu_data.get('name', 'unknown')}")
        
        # Генерируем предупреждение
        warning = generate_weight_control_warning(weight_controls)
        
        # Создаем обновленное сообщение
        updated_message = f"{original_message}\n\n{warning}"
        
        # Создаем клавиатуру с ссылками на карты
        keyboard = create_weight_control_keyboard(
            weight_controls, 
            search_lat=lat, 
            search_lon=lon, 
            search_radius=50
        )
        
        return updated_message, keyboard
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке весового контроля для ПЗУ {pzu_data.get('name', 'unknown')}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return original_message, None


def convert_pzu_tuple_to_dict(pzu_tuple) -> Dict[str, Any]:
    """
    Преобразует кортеж данных ПЗУ из базы данных в словарь
    
    Args:
        pzu_tuple: Кортеж (name, abbreviation, lat, lon, phone)
        
    Returns:
        Словарь с данными ПЗУ
    """
    if not pzu_tuple:
        return {}
    
    return {
        'name': pzu_tuple[1],        # abbreviation - название ПЗУ
        'address': pzu_tuple[0],     # name - адрес
        'latitude': pzu_tuple[2],    # lat - широта
        'longitude': pzu_tuple[3],   # lon - долгота
        'phone': pzu_tuple[4]        # phone - телефон
    }


# Дополнительные обработчики для весового контроля
@router.callback_query(lambda c: c.data.startswith("weight_control_"))
async def handle_weight_control_callback(callback):
    """
    Обработчик callback'ов для весового контроля
    """
    try:
        if callback.data == "weight_control_more":
            # Показать больше пунктов весового контроля
            await callback.answer("Функция в разработке", show_alert=True)
        else:
            await callback.answer("Неизвестная команда", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка в обработчике весового контроля: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
