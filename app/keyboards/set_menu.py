from aiogram import Bot
from aiogram.types import BotCommand
from app.lexicon.lexicon import LEXICON_COMMANDS


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description=LEXICON_COMMANDS["/start"]),
        BotCommand(command="/help", description=LEXICON_COMMANDS["/help"]),
        BotCommand(command="/contacts", description=LEXICON_COMMANDS["/contacts"]),
        BotCommand(command="/donate", description=LEXICON_COMMANDS["/donate"]),
        BotCommand(command="/list_pzu", description=LEXICON_COMMANDS["/list_pzu"]),
    ]
    await bot.set_my_commands(main_menu_commands)
