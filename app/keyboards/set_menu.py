from aiogram import Bot
from aiogram.types import BotCommand



# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands =  [
        BotCommand(command='/start',
                   description='Старт бота'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/contacts',
                   description='Способы связи'),
        BotCommand(command='/list_pzu',
                   description='Список всех ПЗУ')
    ]
    await bot.set_my_commands(main_menu_commands)