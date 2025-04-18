from aiogram.types import CallbackQuery
from aiogram import F
from aiogram import Router

from app.utils.generating_a_reply_message import generating_a_reply_message
from app.database.db import list_directions, list_pzu_in_direction, list_pzu, query_item_in_database, add_id_to_database
from app.keyboards.inline import create_kb_for_direction

import logging

logger = logging.getLogger('lomportbot.callback_directions')

# Логгер для записи в базу данных
db_logger = logging.getLogger('db_logger')

router = Router()

list_d = [i[0] for i in list_directions()]


@router.callback_query(F.data.in_(list_d))
async def process_buttons_directions_press(callback: CallbackQuery):
    # Получить список всех пзу направления полученного из callback.data
    request_result = list_pzu_in_direction(callback.data)
    request_result.sort()

    # Создать клавиатуру со списком ПЗУ
    kb = create_kb_for_direction(callback.data)

    # Отправить сообщение с результатом запроса и клавиатурой
    await callback.message.edit_text(
        text=f'Вы выбрали направление - {callback.data}',
        reply_markup=kb
    )


@router.callback_query(F.data.in_(list_pzu()))
async def process_buttons_pzu_press(callback: CallbackQuery):
    try:
        # Делаем запрос к БД
        # Получаем ответ в виде кортежа
        res_data = query_item_in_database(callback.data.upper())
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
            callback.from_user.id, callback.from_user.username, callback.from_user.full_name, callback.data.upper(),
            extra={
                'user_id': callback.from_user.id,
                'user_name': callback.from_user.username,
                'fullname': callback.from_user.full_name,
                'pzu_name': callback.data.upper(),
            }
        )

    user_id = callback.from_user.id
    add_id_to_database(user_id)
    await callback.message.edit_text(
        text=f'Вот ваше ПЗУ - {callback.data}'
    )
    await callback.message.answer(text=reply_message, parse_mode='HTML')
