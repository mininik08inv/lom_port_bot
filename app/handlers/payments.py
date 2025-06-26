from typing import Optional

import yookassa
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.config_data.config import load_config
from app.keyboards.inline import donat_amount_keyboard, transition_to_payment_keyboard
from app.keyboards.kb import get_cancel_keyboard
import logging

logger = logging.getLogger("lomportbot.payments")

config = load_config()

router = Router()

# Инициализация клиента ЮKassa
yookassa.Configuration.account_id = config.yoo_kassa.account_id
yookassa.Configuration.secret_key = config.yoo_kassa.secret_key


# Создаем состояния для FSM (Finite State Machine)
class DonateState(StatesGroup):
    waiting_for_amount = State()  # Ожидание ввода суммы
    waiting_for_custom_amount = State()  # Ожидание ввода пользовательской суммы


# Обработчик команды /donate
@router.message(Command("donate"))
async def process_donate_command(message: Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} инициировал процесс пожертвования.")
    # Отправляем сообщение с инлайн-клавиатурой для выбора суммы
    await message.answer(
        "Выберите сумму для поддержки:", reply_markup=donat_amount_keyboard()
    )
    # Устанавливаем состояние ожидания ввода суммы
    await state.set_state(DonateState.waiting_for_amount)


# Обработчик команды /donate
@router.callback_query(F.data.in_("/donate"))
async def process_donate_command(callback: CallbackQuery, state: FSMContext):
    logger.info(
        f"User {callback.from_user.id} инициировал процесс пожертвования с помощью  callback."
    )
    # Отправляем сообщение с инлайн-клавиатурой для выбора суммы
    await callback.message.answer(
        "Выберите сумму для поддержки:", reply_markup=donat_amount_keyboard()
    )
    # Устанавливаем состояние ожидания ввода суммы
    await state.set_state(DonateState.waiting_for_amount)
    # Подтверждаем обработку callback-запроса
    await callback.answer()


# Обработчик выбора суммы
@router.callback_query(DonateState.waiting_for_amount, F.data.startswith("amount_"))
async def process_amount(callback: CallbackQuery, state: FSMContext):
    amount = int(callback.data.split("_")[1])
    logger.info(f"User {callback.from_user.id} выбрал сумму: {amount} RUB.")
    await state.update_data(amount=amount)
    await create_payment(
        amount, user_id=callback.from_user.id, message=callback.message
    )
    await callback.answer()


# Обработчик выбора "Другая сумма"
@router.callback_query(DonateState.waiting_for_amount, F.data == "custom_amount")
async def process_custom_amount(callback: CallbackQuery, state: FSMContext):
    logger.info(f"User {callback.from_user.id} выбрал пользовательскую сумму.")
    # Запрашиваем ввод суммы вручную
    await callback.message.answer("Введите сумму в рублях (например, 300):")
    await state.set_state(DonateState.waiting_for_custom_amount)
    await callback.answer()


# Обработчик ручного ввода суммы
@router.message(
    DonateState.waiting_for_custom_amount,
    ~F.text.in_(["❌ Отмена"]),  # Сначала проверяем отмену
)
async def process_amount_input(message: Message, state: FSMContext):
    # Проверка на число
    if message.text.isdigit():
        amount = int(message.text)
        if 10 <= amount <= 100000:
            await create_payment(amount, message.from_user.id, message)
            return
        await message.answer("Сумма должна быть от 10 до 100 000 руб.")
    else:
        await message.answer("Введите только цифры (например: 100)")

    # Повторно показываем клавиатуру с отменой
    await message.answer("Попробуйте ещё раз:", reply_markup=get_cancel_keyboard())


# Обработчик отмены
@router.message(DonateState.waiting_for_custom_amount, F.text == "❌ Отмена")
async def cancel_input(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод суммы отменён!", reply_markup=ReplyKeyboardRemove())
    logger.info(f"User {message.from_user.id} отменил ввод суммы")


# Для обработки отмены
@router.message(DonateState.waiting_for_custom_amount, F.text == "❌ Отмена")
async def cancel_amount_input(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод суммы отменён.", reply_markup=ReplyKeyboardRemove())


# Обработчик некорректного ввода
@router.message(DonateState.waiting_for_custom_amount)
async def process_invalid_amount(message: Message):
    logger.warning(f"User {message.from_user.id} ввёл неверную сумму: {message.text}.")
    await message.answer(
        "Пожалуйста, введите корректную сумму (только цифры, например, 300)."
    )


# Функция для создания платежа
async def create_payment(amount: int, user_id: int, message: Optional[Message] = None):
    try:
        deep_link = (
            f"https://t.me/lom_port_bot?payment_success=payment_success_{amount}"
        )

        payment = yookassa.Payment.create(
            {
                "amount": {"value": f"{amount}.00", "currency": "RUB"},
                "confirmation": {"type": "redirect", "return_url": deep_link},
                "capture": True,
                "description": "Донат для бота",
                "metadata": {
                    "user_id": str(user_id),  # Сохраняем ID в metadata
                    "skip_receipt": "true",
                },
            }
        )

        url = payment.confirmation.confirmation_url
        kb = transition_to_payment_keyboard(url)

        if message:
            await message.answer(
                "Нажмите кнопку ниже для перехода к оплате:", reply_markup=kb
            )
        else:
            # Если message=None (например, при вызове из callback), логируем ошибку
            logger.warning(f"Сообщение недоступно для user_id={user_id}")

        logger.info(
            f"Платеж создан | User: {user_id} | Сумма: {amount} RUB | URL: {url}"
        )

    except Exception as e:
        logger.error(f"Ошибка платежа | User: {user_id} | Error: {e}")
        if message:
            await message.answer("Ошибка при создании платежа. Попробуйте позже.")


# Благодарность за поддержку
@router.message(Command("payment_success"))
async def process_start_command(message: Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("payment_success_"):
        amount = args[1].split("_")[2]
        await message.answer(f"Спасибо за вашу поддержку в размере {amount} рублей! 🎉")
    else:
        await message.answer(
            "Добро пожаловать! Используйте /donate для поддержки бота."
        )
