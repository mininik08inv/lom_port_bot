from aiogram.types import Message, ChatMemberUpdated, ContentType
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram import F
from aiogram import Router

from app.utils.generating_a_reply_message import generating_a_reply_message
from app.database.db import query_item_in_database, get_db_connection, add_id_to_database, delete_id_to_database
from app.keyboards.inline import create_kb_for_help, create_kb_for_contacts, create_kb_for_list_pzu
from app.lexicon.lexicon import LEXICON

import logging

logger = logging.getLogger('lomportbot.commands')

# Логгер для записи в базу данных
db_logger = logging.getLogger('db_logger')

router = Router()


# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    # Проверяем, есть ли payload в команде /start
    if len(message.text.split()) > 1:
        payload = message.text.split()[1]  # Получаем payload (например, "payment_success_100")
        if payload.startswith("payment_success_"):
            amount = payload.split("_")[2]  # Извлекаем сумму
            await message.answer(f"Спасибо за вашу поддержку в размере {amount} рублей! 🎉")
    else:
        # Добавляем id в базу если еще нет
        user_id = message.from_user.id
        add_id_to_database(user_id)

        logger.info(
            f"Пользователь {user_id}, user_name: {message.from_user.username} - запустил бота"
        )
        await message.answer(text=LEXICON['/start'])


# Этот хэндлер будет срабатывать на команду "/help"
async def process_help_command(message: Message):
    await message.answer(
        text=LEXICON['/help'],
        reply_markup=create_kb_for_help()
    )


# Этот хэндлер будет срабатывать на команду "/contacts"
async def process_contacts_command(message: Message):
    await message.answer(
        text=LEXICON['/contacts'],
        reply_markup=create_kb_for_contacts()
    )


# Этот хэндлер будет срабатывать на команду "/list_pzu"
async def process_list_pzu_command(message: Message):
    # logger.info("User: %s, user_name: %s запросил список пзу", {message.from_user.id}, {message.from_user.username})
    kb = create_kb_for_list_pzu()
    await message.answer(
        text='Вот список направлений, выбирай.',
        reply_markup=kb
    )


# Этот хэндлер будет срабатывать на отправку боту фото
async def if_the_photo(message: Message):
    logger.info(
        f"Пользователь с id: {message.from_user.id}, user_name: {message.from_user.username}, fullname: {message.from_user.full_name} отправил фото"
    )

    # await message.reply_photo(message.photo[0].file_id)
    await message.answer("Я конечно люблю картики посмотреть, но не на работе!")


# Этот хэндлер будет срабатывать на отправку боту стикера
async def if_the_sticker(message: Message):
    # await message.reply_photo(message.photo[0].file_id)
    await message.answer("Стикеры 😏, это не совсем то, что нужно!")


# Этот хэндлер будет срабатывать на отправку боту голосового сообщения
async def if_the_voice(message: Message):
    await message.answer(
        text="Вы прислали голосовое сообщение! А я пока что работаю только с текстом😔"
    )


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
async def send_point(message: Message):
    try:
        # Делаем запрос к БД
        # Получаем ответ в виде кортежа
        res_data = query_item_in_database(message.text.upper().replace(" ", "").replace("-", ""))
        # Передаем  полученный кортеж в функцию
        if res_data:
            reply_message = generating_a_reply_message(res_data)
        else:
            reply_message = LEXICON['not_found']

    except Exception as e:
        # Обработка ошибок
        logger.exception("Какая то ошибка", e, message)

    finally:
        logger.info(
            f'User id:{message.from_user.id}, user_name:{message.from_user.username}, fullname:{message.from_user.full_name} запросил ПЗУ: "{message.text.upper()}"'
        )
        # Запись в базу данных
        db_logger.info(
            'User id:%s, user_name:%s, fullname:%s запросил ПЗУ: "%s"',
            message.from_user.id, message.from_user.username, message.from_user.full_name, message.text.upper(),
            extra={
                'user_id': message.from_user.id,
                'user_name': message.from_user.username,
                'fullname': message.from_user.full_name,
                'pzu_name': message.text.upper(),
            }
        )

    # Добавляем id в базу если еще нет
    user_id = message.from_user.id
    add_id_to_database(user_id)

    await message.answer(text=reply_message, parse_mode="HTML")


# Этот хэндлер будет срабатывать на блокировку бота пользователем
async def process_user_blocked_bot(event: ChatMemberUpdated):
    new_status = event.new_chat_member.status

    # Проверяем, был ли пользователь удален или заблокировал бота
    if new_status in ("left", "kicked"):
        user_id = event.from_user.id
        username = event.from_user.username

        logger.warning(f"Пользователь {user_id}, user_name: {username} - заблокировал бота")

        # Удаляем пользователя из базы данных
        delete_id_to_database(user_id)


# Этот хэндлер будет срабатывать когда бота расблокировали
async def process_user_unblocked_bot(event: ChatMemberUpdated):
    user_id = event.from_user.id

    db_conn = get_db_connection()
    with db_conn.cursor() as cur:
        try:
            # Удаляем пользователя из базы данных
            cur.execute("DELETE FROM telegram_bot_users WHERE user_id = %s", (user_id,))
            db_conn.commit()
        except Exception as e:
            logger.exception("Ошибка при удалении user_id из бд: %s", e)

    logger.warning(
        f"Пользователь {user_id}, user_name: {event.from_user.username} - РАЗблокировал бота"
    )


# Этот хедрлер будет срабатывать на любые не обрабатываемы типы контента в апдейте
async def if_something_else(message: Message):
    await message.answer(
        "Видео, Аудио, Документы, Игры и т.д меня мало интересуют😏, текст и только текст!"
    )


# Регистрируем хэндлеры
router.message.register(process_start_command, Command(commands="start"))
router.message.register(process_help_command, Command(commands="help"))
router.message.register(process_contacts_command, Command(commands="contacts"))
router.message.register(process_list_pzu_command, Command(commands="list_pzu"))
router.message.register(if_the_photo, F.content_type == ContentType.PHOTO)
router.message.register(if_the_sticker, F.content_type == ContentType.STICKER)
router.message.register(if_the_voice, F.content_type == ContentType.VOICE)
router.message.register(
    if_something_else,
    F.content_type.in_(
        {
            ContentType.ANIMATION,
            ContentType.VIDEO,
            ContentType.VIDEO_NOTE,
            ContentType.AUDIO,
            ContentType.DOCUMENT,
            ContentType.GAME,
            ContentType.UNKNOWN,
            ContentType.ANY,
        }
    ),
)
router.my_chat_member.register(
    process_user_blocked_bot, ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
router.my_chat_member.register(
    process_user_unblocked_bot, ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
router.message.register(send_point)
