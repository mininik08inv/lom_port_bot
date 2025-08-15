"""
Хендлеры для работы с пунктами весового контроля
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from typing import List, Dict, Tuple

from app.services.weight_control_service import WeightControlService
from app.utils.map_utils import (
    generate_weight_control_warning
)
from app.keyboards.inline import create_weight_control_keyboard
import logging

logger = logging.getLogger("lomportbot.weight_control_handlers")

router = Router()


async def check_weight_control_near_pzu(
    pzu_coordinates: Tuple[float, float], 
    pzu_name: str = "ПЗУ",
    radius_km: int = 100
) -> Tuple[bool, str, List[Dict]]:
    """
    Проверяет наличие пунктов весового контроля рядом с ПЗУ
    
    Args:
        pzu_coordinates: Кортеж (широта, долгота) ПЗУ
        pzu_name: Название ПЗУ для логирования
        radius_km: Радиус поиска в километрах
        
    Returns:
        Кортеж (найдены_ли_пункты, текст_предупреждения, список_пунктов)
    """
    try:
        pzu_lat, pzu_lon = pzu_coordinates
        
        # Поиск пунктов весового контроля
        weight_controls = await WeightControlService.find_nearby_weight_control(
            pzu_lat, pzu_lon, radius_km
        )
        
        if weight_controls:
            warning_text = generate_weight_control_warning(weight_controls)
            logger.info(f"Найдено {len(weight_controls)} пунктов весового контроля "
                       f"рядом с {pzu_name}")
            return True, warning_text, weight_controls
        else:
            logger.info(f"Пунктов весового контроля рядом с {pzu_name} не найдено")
            return False, "", []
            
    except Exception as e:
        logger.error(f"Ошибка при проверке весового контроля для {pzu_name}: {e}")
        return False, "Ошибка при проверке пунктов весового контроля", []


@router.message(Command("weight_control_stats"))
async def cmd_weight_control_stats(message: Message):
    """Показывает статистику по пунктам весового контроля"""
    try:
        stats = await WeightControlService.get_stats()
        
        text = "📊 Статистика пунктов весового контроля:\n\n"
        text += f"📍 Всего пунктов: {stats['total_points']}\n"
        text += f"🗺️ С координатами: {stats['points_with_coordinates']}\n"
        
        if stats['points_with_coordinates'] > 0:
            percentage = (stats['points_with_coordinates'] / stats['total_points']) * 100
            text += f"📈 Процент покрытия: {percentage:.1f}%\n"
        
        if stats['top_regions']:
            text += "\n🏆 Топ регионов по количеству пунктов:\n"
            for i, region_info in enumerate(stats['top_regions'][:5], 1):
                text += f"{i}. Регион {region_info['region']}: {region_info['count']} пунктов\n"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await message.answer("❌ Ошибка при получении статистики")


@router.callback_query(F.data.startswith("weight_control_info:"))
async def callback_weight_control_info(callback: CallbackQuery):
    """Показывает детальную информацию о пункте весового контроля"""
    try:
        # Извлекаем ID пункта из callback_data
        # external_id = callback.data.split(":")[1]
        
        # Здесь можно добавить запрос к БД для получения полной информации
        # conn = await get_db_connection()
        # point_info = await conn.fetchrow(
        #     "SELECT * FROM weight_control_points WHERE external_id = $1", external_id
        # )
        
        await callback.answer("ℹ️ Детальная информация о пункте")
        
    except Exception as e:
        logger.error(f"Ошибка при получении информации о пункте: {e}")
        await callback.answer("❌ Ошибка при получении информации")


@router.callback_query(F.data.startswith("wc_more:"))
async def callback_weight_control_show_all(callback: CallbackQuery):
    """Показывает все пункты весового контроля в области поиска"""
    try:
        # Парсим координаты из callback_data: "wc_more:lat:lon:radius"
        data_parts = callback.data.split(":")
        if len(data_parts) != 4:
            await callback.answer("❌ Ошибка в данных поиска")
            return
        
        lat = float(data_parts[1])
        lon = float(data_parts[2])
        radius = int(data_parts[3])
        
        # Выполняем поиск всех пунктов
        weight_controls = await WeightControlService.find_nearby_weight_control(
            lat, lon, radius
        )
        
        if weight_controls:
            # Формируем детальный список всех пунктов
            points_text = f"📍 **Все пункты весового контроля в радиусе {radius} км:**\n\n"
            
            for i, wc in enumerate(weight_controls, 1):
                distance = round(wc['distance'], 1)
                region = wc.get('region', 'Не указан')
                points_text += f"{i}. **{wc['name']}**\n"
                points_text += f"   📍 {distance} км • {region}\n"
                if wc.get('latitude') and wc.get('longitude'):
                    points_text += f"   🗺️ {wc['latitude']}, {wc['longitude']}\n"
                points_text += "\n"
            
            # Создаем клавиатуру с картами (ограничиваем до 10 кнопок для удобства)
            keyboard_controls = weight_controls[:10] if len(weight_controls) > 10 else weight_controls
            keyboard = create_weight_control_keyboard(keyboard_controls, lat, lon, radius)
            
            # Отправляем новое сообщение со всеми пунктами
            await callback.message.answer(
                points_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
            
            await callback.answer("📋 Показаны все найденные пункты")
            
        else:
            await callback.answer("❌ Пункты не найдены")
        
    except Exception as e:
        logger.error(f"Ошибка при показе всех пунктов: {e}")
        await callback.answer("❌ Ошибка при загрузке данных")


@router.callback_query(F.data == "weight_control_more_info")
async def callback_weight_control_more_info_fallback(callback: CallbackQuery):
    """Fallback для старого формата кнопки"""
    try:
        await callback.answer(
            "ℹ️ Показаны только ближайшие 5 пунктов весового контроля.\n\n"
            "🔍 Для поиска всех пунктов используйте:\n"
            "/find_weight_control широта долгота радиус\n\n"
            "Например: /find_weight_control 55.7558 37.6173 50",
            show_alert=True
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке 'еще пунктов': {e}")
        await callback.answer("❌ Ошибка")


@router.message(Command("find_weight_control"))
async def cmd_find_weight_control(message: Message):
    """
    Команда для поиска пунктов весового контроля по координатам
    Формат: /find_weight_control широта долгота [радиус]
    """
    try:
        # Парсим аргументы команды
        args = message.text.split()[1:]  # Убираем саму команду
        
        if len(args) < 2:
            await message.answer(
                "❌ Неверный формат команды!\n\n"
                "Используйте: /find_weight_control широта долгота [радиус]\n"
                "Пример: /find_weight_control 55.7558 37.6173 30"
            )
            return
        
        # Получаем координаты
        lat = float(args[0])
        lon = float(args[1])
        radius = int(args[2]) if len(args) > 2 else 50
        
        # Валидация координат
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            await message.answer("❌ Некорректные координаты!")
            return
            
        if not (1 <= radius <= 200):
            await message.answer("❌ Радиус должен быть от 1 до 200 км!")
            return
        
        # Поиск пунктов
        await message.answer("🔍 Ищем пункты весового контроля...")
        
        weight_controls = await WeightControlService.find_nearby_weight_control(
            lat, lon, radius
        )
        
        if weight_controls:
            warning_text = generate_weight_control_warning(weight_controls)
            keyboard = create_weight_control_keyboard(weight_controls, lat, lon, radius)
            
            await message.answer(
                f"📍 Поиск в радиусе {radius} км от координат {lat}, {lon}\n\n{warning_text}",
                reply_markup=keyboard
            )
        else:
            await message.answer(
                f"✅ В радиусе {radius} км от указанных координат "
                f"пунктов весового контроля не найдено"
            )
        
    except ValueError:
        await message.answer("❌ Некорректные числовые значения!")
    except Exception as e:
        logger.error(f"Ошибка при поиске пунктов весового контроля: {e}")
        await message.answer("❌ Ошибка при поиске пунктов весового контроля")


async def add_weight_control_check_to_pzu_response(
    pzu_data: Dict,
    original_text: str
) -> Tuple[str, object]:
    """
    Добавляет проверку весового контроля к ответу о ПЗУ
    
    Args:
        pzu_data: Данные о ПЗУ (должны содержать latitude, longitude)
        original_text: Исходный текст ответа о ПЗУ
        
    Returns:
        Кортеж (обновленный_текст, клавиатура_или_None)
    """
    try:
        # Проверяем наличие координат ПЗУ (pzu_data это кортеж: [0]=id, [1]=name, [2]=lat, [3]=lng, [4]=phone, ...)
        if len(pzu_data) < 4 or not pzu_data[2] or not pzu_data[3]:
            return original_text, None
        
        pzu_coordinates = (float(pzu_data[2]), float(pzu_data[3]))  # lat, lng
        pzu_name = pzu_data[1] if len(pzu_data) > 1 and pzu_data[1] else 'ПЗУ'
        
        # Проверяем весовой контроль
        has_weight_control, warning_text, weight_controls = await check_weight_control_near_pzu(
            pzu_coordinates, pzu_name
        )
        
        if has_weight_control:
            # Добавляем предупреждение к исходному тексту
            updated_text = f"{original_text}\n\n{warning_text}"
            
            # Создаем клавиатуру со ссылками на карты (передаем координаты ПЗУ как центр поиска)
            keyboard = create_weight_control_keyboard(
                weight_controls, 
                pzu_coordinates[0],  # latitude
                pzu_coordinates[1],  # longitude
                50  # радиус по умолчанию
            )
            
            return updated_text, keyboard
        else:
            return original_text, None
            
    except Exception as e:
        logger.error(f"Ошибка при добавлении проверки весового контроля: {e}")
        return original_text, None
