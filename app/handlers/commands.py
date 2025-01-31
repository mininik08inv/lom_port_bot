from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import Message
from aiogram.types import ChatMemberUpdated

from app.utils.generating_a_reply_message import generating_a_reply_message
from app.database.db import get_db_connection

import logging.config
from app.loggs.logging_setting import logging_config
from dotenv import load_dotenv

load_dotenv()

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)
print(logger)


# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    logger.info(f'Пользователь {message.from_user.id}, user_name: {message.from_user.username} - запустил бота')
    await message.answer('Привет!\nМеня зовут LomPortBot!\nЯ могу помочь вам с поиском ПЗУ\n')


# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: Message):
    await message.answer(
        f'''Напиши мне название нужного ПЗУ \nЯ пришлю тебе информацию о нем, если она есть в моей базе!\n Формат должен быть таким: вп1, ВП1, Вп1 или например Ворсино. \n Список доступных ПЗУ здесь /list_pzu \nБудет время посетите мой сайт https://lomovoz-portal.ru/'''
    )


# Этот хэндлер будет срабатывать на команду "/list_pzu"
async def process_list_pzu_command(message: Message):
    try:
        # Подключение к базе данных
        db_conn = get_db_connection()
        with db_conn.cursor() as cur:
            sql_query = f"select abbreviation from points_location"
            # Делаем запрос к БД
            try:
                # Делаем запрос в базу данных
                cur.execute(sql_query)
                # Получаем ответ в виде списка кортежей
                res_data = cur.fetchall()
                # Преобразуем в одномерный список
                reply_message = [i[0] for i in res_data]
                # Сортируем список по алфавиту
                reply_message.sort()
                # Преобразуем список в строку со сзачениями разделенными запятой
                reply_message = ', '.join(reply_message)

            except:
                logger.exception('Какая то ошибка в обработчике /list_pzu')
                reply_message = f'Возможно вы ввели не верные данные или этого ПЗУ нет в базе!\n Инструкция здесь - /help'


    except Exception as e:
        # Обработка ошибок
        logger.exception('Какая то ошибка в обработчике /list_pzu')

    finally:
        # Закрытие соединения с базой данных
        if db_conn:
            db_conn.close()

    logger.info(
        f'Пользователь с id: {message.from_user.id}, user_name: {message.from_user.username}, fullname: {message.from_user.full_name}  запросил список ПЗУ')

    await message.answer(text=reply_message)


# Этот хэндлер будет срабатывать на отправку боту фото
async def if_the_photo(message: Message):
    logger.info(
        f'Пользователь с id: {message.from_user.id}, user_name: {message.from_user.username}, fullname: {message.from_user.full_name} отправил фото')

    # await message.reply_photo(message.photo[0].file_id)
    await message.answer(f'Я конечно люблю картики посмотреть, но не на работе!')


# Этот хэндлер будет срабатывать на отправку боту стикера
async def if_the_sticker(message: Message):
    # await message.reply_photo(message.photo[0].file_id)
    await message.answer(f'Стикеры 😏, это не совсем то, что нужно!')


# Этот хэндлер будет срабатывать на отправку боту голосового сообщения
async def if_the_voice(message: Message):
    await message.answer(text='Вы прислали голосовое сообщение! А я пока что работаю только с текстом😔')


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
async def send_point(message: Message):
    try:
        # Подключение к базе данных
        db_conn = get_db_connection()
        with db_conn.cursor() as cur:
            sql_query = f"SELECT * FROM points_location WHERE abbreviation='{message.text.upper()}'"
            # Делаем запрос к БД
            try:
                cur.execute(sql_query)
                # Получаем ответ в виде кортежа
                res_data = cur.fetchone()
                # Передаем  полученный кортеж в функцию пуе
                reply_message = generating_a_reply_message(res_data)
            except:
                reply_message = f'Возможно вы ввели не верные данные или этого ПЗУ нет в базе!\n Инструкция здесь - /help'


    except Exception as e:
        # Обработка ошибок
        logger.exception('Какая то ошибка')

    finally:
        # Закрытие соединения с базой данных
        if db_conn:
            db_conn.close()
            logger.info(
                f'Пользователь с id:{message.from_user.id}, user_name: {message.from_user.username},fullname : {message.from_user.full_name}  запросил ПЗУ: "{message.text.upper()}"')
    await message.answer(text=reply_message, parse_mode='HTML')


# Этот хэндлер будет срабатывать на блокировку бота пользователем
async def process_user_blocked_bot(event: ChatMemberUpdated):
    logger.warning(f'Пользователь {event.from_user.id}, user_name: {event.from_user.username} - заблокировал бота')

# Этот хэндлер будет срабатывать когда бота расблокировали
async def process_user_unblocked_bot(event: ChatMemberUpdated):
    logger.warning(f'Пользователь {event.from_user.id}, user_name: {event.from_user.username} - РАЗблокировал бота')


# Этот хедрлер будет срабатывать на любые не обрабатываемы типы контента в апдейте
async def if_something_else(message: Message):
    await message.answer(f'Видео, Аудио, Документы, Игры и т.д меня мало интересуют😏, текст и только текст!')
