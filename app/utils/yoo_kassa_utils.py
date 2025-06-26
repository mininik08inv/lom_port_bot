import yookassa
import logging.config

from app.loggs.logging_setting import logging_config


logging.config.dictConfig(logging_config)

logger = logging.getLogger("lomportbot")


async def check_payment_status(payment_id: str):
    try:
        payment = yookassa.Payment.find_one(payment_id)
        return payment.status  # "succeeded", "waiting_for_capture", "canceled"
    except Exception as e:
        logger.error(f"Ошибка при проверке платежа {payment_id}: {e}")
        return None
