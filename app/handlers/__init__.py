"""
Инициализация хендлеров бота
Включает импорт всех роутеров включая новые для весового контроля
"""

from aiogram import Router
from . import (
    commands,
    callback_directions, 
    admin_commands,
    payments,
    weight_control_handlers  # Новый модуль для весового контроля
)

def setup_routers() -> Router:
    """
    Настройка и объединение всех роутеров бота
    
    Returns:
        Главный роутер со всеми подключенными хендлерами
    """
    # Создаем главный роутер
    main_router = Router()
    
    # Подключаем существующие роутеры
    main_router.include_router(commands.router)
    main_router.include_router(callback_directions.router)
    main_router.include_router(admin_commands.router)
    main_router.include_router(payments.router)
    
    # Подключаем новый роутер для весового контроля
    main_router.include_router(weight_control_handlers.router)
    
    return main_router
