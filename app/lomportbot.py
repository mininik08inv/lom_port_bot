import os
import requests
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ContentType
from aiogram import F
from aiogram.filters import ChatMemberUpdatedFilter, KICKED
from aiogram.types import ChatMemberUpdated
from database.db import get_db_connection

import logging.config
from loggs.logging_setting import logging_config

load_dotenv()
logging.config.dictConfig(logging_config)
logger = logging.getLogger('bot')

# BOT_TOKEN = os.environ.get('TELEGRAM_TOKEN')
BOT_TOKEN = os.environ.get('COURSE_TEST_BOT_TOKEN')

# Создаем объекты бота и диспетчера
dp: Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def generating_a_reply_message(point):
    # url = f'https://yandex.ru/navi?whatshere%5Bpoint%5D={point[4]}%2C{point[3]}&whatshere%5Bzoom%5D=12'
    url = f'https://yandex.ru/navi?whatshere%5Bpoint%5D={point[4]}%2C{point[3]}&whatshere%5Bzoom%5D=16.768925&ll={point[4]}%2C{point[3]}&z=16.768925&si=e5wmhgefmj352468jpym3ewa4m'
    weather = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={point[3]}&longitude={point[4]}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")

    reply_message = f'''Запрашиваемый пункт: {point[2]}
                 \nАдрес: {point[1]}
                 \nКоординаты: {url}
                 \nНомер телефона: {point[-2]}
                 \nПогода в районе погрузки😄: температура воздуха : {weather.json()['current']['temperature_2m']}'''

    return reply_message


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
    await message.reply(text=reply_message)


# Этот хэндлер будет срабатывать на блокировку бота пользователем
@dp.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated):
    logger.warning(f'Пользователь {event.from_user.id}, user_name: {event.from_user.username} - заблокировал бота')


# Этот хедрлер будет срабатывать на любые не обрабатываемы типы контента в апдейте
async def if_something_else(message: Message):
    await message.answer(f'Видео, Аудио, Документы, Игры и т.д меня мало интересуют😏, текст и только текст!')


# Регистрируем хэндлеры
dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(process_list_pzu_command, Command(commands='list_pzu'))
dp.message.register(if_the_photo, F.content_type == ContentType.PHOTO)
dp.message.register(if_the_sticker, F.content_type == ContentType.STICKER)
dp.message.register(if_the_voice, F.content_type == ContentType.VOICE)
dp.message.register(if_something_else, F.content_type.in_({ContentType.VIDEO_NOTE,
                                                           ContentType.AUDIO,
                                                           ContentType.DOCUMENT,
                                                           ContentType.GAME,
                                                           ContentType.UNKNOWN,
                                                           ContentType.ANY
                                                           }))
dp.message.register(send_point)

if __name__ == '__main__':
    dp.run_polling(bot)
