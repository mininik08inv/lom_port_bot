
from aiogram.types import CallbackQuery
from aiogram import Router

from app.filters.my_filters import direction_filter, pzu_filter
from app.utils.generating_a_reply_message import generating_a_reply_message
from app.database.db import (
    list_pzu_in_direction,
    query_item_in_database,
    add_id_to_database,
)
from app.keyboards.inline import create_kb_for_direction

import logging

logger = logging.getLogger("lomportbot.callback_directions")

# Логгер для записи в базу данных
db_logger = logging.getLogger("db_logger")

router = Router()


@router.callback_query(direction_filter)
async def process_buttons_directions_press(callback: CallbackQuery):
    try:
        # Получаем и сортируем список ПЗУ
        pzu_list = await list_pzu_in_direction(callback.data)
        pzu_list.sort()  # Сортируем по алфавиту

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
    try:
        # Делаем запрос к БД
        # Получаем ответ в виде asincpg.Record
        res_data = await query_item_in_database(callback.data.upper())
        # Передаем  полученный кортеж в функцию
        if res_data:
            reply_message = generating_a_reply_message(res_data)
        else:
            reply_message = "Возможно вы ввели не верные данные или этого ПЗУ нет в базе!\n Инструкция здесь - /help а подробности в Меню"

    except Exception as e:
        # Обработка ошибок
        logger.exception("Какая то ошибка", e)

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
    user_id = callback.from_user.id
    await add_id_to_database(user_id)
    await callback.message.edit_text(text=f"Вот ваше ПЗУ - {callback.data}")
    await callback.message.answer(text=reply_message, parse_mode="HTML")
