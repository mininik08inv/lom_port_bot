
from aiogram.types import CallbackQuery
from aiogram import Router

from app.filters.my_filters import direction_filter, pzu_filter
from app.utils.generating_a_reply_message import generating_a_reply_message
from app.database.db import (
    query_item_in_database,
    add_id_to_database,
)
from app.keyboards.inline import create_kb_for_direction
from app.handlers.weight_control_handlers import add_weight_control_check_to_pzu_response

import logging

logger = logging.getLogger("lomportbot.callback_directions")

# Логгер для записи в базу данных
db_logger = logging.getLogger("db_logger")

router = Router()


@router.callback_query(direction_filter)
async def process_buttons_directions_press(callback: CallbackQuery):
    try:
        # Создаем клавиатуру
        kb = await create_kb_for_direction(callback.data)

        # Редактируем сообщение
        await callback.message.edit_text(
            text=f"Вы выбрали направление: {callback.data}", reply_markup=kb
        )

        # Подтверждаем обработку callback
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка обработки направления {callback.data}: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(pzu_filter)
async def process_buttons_pzu_press(callback: CallbackQuery):
    reply_message = None
    try:
        # Делаем запрос к БД
        # Получаем ответ в виде asincpg.Record
        res_data = await query_item_in_database(callback.data.upper())
        # Передаем  полученный кортеж в функцию
        if res_data:
            reply_message = await generating_a_reply_message(res_data)
        else:
            reply_message = "Возможно вы ввели не верные данные или этого ПЗУ нет в базе!\n Инструкция здесь - /help а подробности в Меню"

        # Добавляем пользователя в базу данных
        user_id = callback.from_user.id
        await add_id_to_database(user_id)
        
        # Отправляем первое сообщение
        await callback.message.edit_text(text=f"Вот ваше ПЗУ - {callback.data}")
        
        # Проверяем весовой контроль если ПЗУ найден
        if res_data:
            try:
                updated_message, weight_keyboard = await add_weight_control_check_to_pzu_response(
                    res_data, reply_message
                )
                
                if weight_keyboard:
                    # Есть весовой контроль - отправляем с предупреждением и кнопками
                    await callback.message.answer(text=updated_message, reply_markup=weight_keyboard, parse_mode="HTML")
                else:
                    # Весового контроля нет - обычная отправка
                    await callback.message.answer(text=reply_message, parse_mode="HTML")
            except Exception as e:
                # Если ошибка в проверке весового контроля - отправляем обычный ответ
                logger.warning(f"Ошибка при проверке весового контроля для callback: {e}")
                await callback.message.answer(text=reply_message, parse_mode="HTML")
        else:
            # ПЗУ не найден - обычная отправка
            await callback.message.answer(text=reply_message, parse_mode="HTML")
        
        await callback.answer()

    except Exception as e:
        # Обработка ошибок
        logger.exception("Ошибка при обработке ПЗУ %s: %s", callback.data.upper(), e)
        await callback.answer("Произошла ошибка при обработке запроса", show_alert=True)

    finally:
        logger.info(
            f'User id:{callback.from_user.id}, user_name:{callback.from_user.username}, fullname:{callback.from_user.full_name}  запросил ПЗУ: "{callback.data.upper()}"'
        )
        # Запись в базу данных
        db_logger.info(
            'User id:%s, user_name:%s, fullname:%s запросил ПЗУ: "%s"',
            callback.from_user.id,
            callback.from_user.username,
            callback.from_user.full_name,
            callback.data.upper(),
            extra={
                "user_id": callback.from_user.id,
                "user_name": callback.from_user.username,
                "fullname": callback.from_user.full_name,
                "pzu_name": callback.data.upper(),
            },
        )
