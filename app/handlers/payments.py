import yookassa
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keyboards.inline import donat_amount_keyboard, transition_to_payment_keyboard
import logging

logger = logging.getLogger('lomportbot.pyments')

router = Router()

# Инициализация клиента ЮKassa
yookassa.Configuration.account_id = '1055012'
yookassa.Configuration.secret_key = 'test_S4EZprxQ53dIWH0FPO9zCOVd1iWYxems8KqrGcP0yA0'


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
        "Выберите сумму для поддержки:",
        reply_markup=donat_amount_keyboard()
    )
    # Устанавливаем состояние ожидания ввода суммы
    await state.set_state(DonateState.waiting_for_amount)


# Обработчик команды /donate
@router.callback_query(F.data.in_('/donate'))
async def process_donate_command(callback: CallbackQuery, state: FSMContext):
    logger.info(f"User {callback.from_user.id} инициировал процесс пожертвования с помощью  callback.")
    # Отправляем сообщение с инлайн-клавиатурой для выбора суммы
    await callback.message.answer(
        "Выберите сумму для поддержки:",
        reply_markup=donat_amount_keyboard()
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
    # Сохраняем сумму в состоянии
    await state.update_data(amount=amount)
    await create_payment(callback.message, amount)
    await callback.answer()


# Обработчик выбора "Другая сумма"
@router.callback_query(DonateState.waiting_for_amount, F.data == "custom_amount")
async def process_custom_amount(callback: CallbackQuery, state: FSMContext):
    logger.info(f"User {callback.from_user.id} выбрал пользовательскую сумму.")
    # Запрашиваем ввод суммы вручную
    await callback.message.answer("Введите сумму в рублях (например, 300):")
    await state.set_state(DonateState.waiting_for_custom_amount)
    await callback.answer()


# Обработчик ввода суммы вручную
@router.message(DonateState.waiting_for_custom_amount, F.text.regexp(r"^\d+$"))
async def process_custom_amount_input(message: Message, state: FSMContext):
    amount = int(message.text)  # Получаем сумму от пользователя
    logger.info(f"User {message.from_user.id} ввел пользовательскую сумму: {amount} RUB.")
    # Сохраняем сумму в состоянии
    await state.update_data(amount=amount)
    # Создаем платеж с выбранным методом оплаты
    await create_payment(message, amount)
    # Устанавливаем состояние ожидания выбора метода оплаты


# Обработчик некорректного ввода
@router.message(DonateState.waiting_for_custom_amount)
async def process_invalid_amount(message: Message):
    logger.warning(f"User {message.from_user.id} ввёл неверную сумму: {message.text}.")
    await message.answer("Пожалуйста, введите корректную сумму (только цифры, например, 300).")


# Функция для создания платежа
async def create_payment(message: Message, amount: int):
    try:
        # Создаем Deep Link для возврата в бота
        deep_link = f"https://t.me/course_stepik_test_bot?payment_success=payment_success_{amount}"

        # Создание платежа в ЮKassa
        payment = yookassa.Payment.create({
            "amount": {
                "value": f"{amount}.00",  # Сумма в формате "100.00"
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",  # Указываем тип подтверждения
                "return_url": deep_link  # Используем Deep Link для возврата в бота
            },
            "capture": True,
            "description": "Донат для бота"
        })
        url = payment.confirmation.confirmation_url
        kb = transition_to_payment_keyboard(url)
        # Отправка ссылки на оплату пользователю
        await message.answer("Нажмите кнопку ниже для перехода к оплате:", reply_markup=kb)
        logger.info(
            f"Платеж, созданный для пользователя {message.from_user.id} с количеством {amount} RUB. Payment URL: {url}")
    except Exception as e:
        logger.error(f"Не удалось создать платеж для пользователя {message.from_user.id}. Error: {e}")
        await message.answer("Произошла ошибка при создании платежа. Пожалуйста, попробуйте позже.")


# Благодарность за поддержку
@router.message(Command("payment_success"))
async def process_start_command(message: Message):
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("payment_success_"):
        amount = args[1].split("_")[2]
        await message.answer(f"Спасибо за вашу поддержку в размере {amount} рублей! 🎉")
    else:
        await message.answer("Добро пожаловать! Используйте /donate для поддержки бота.")

