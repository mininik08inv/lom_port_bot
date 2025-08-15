from aiogram.utils.markdown import hlink

import logging

from app.utils.weather import get_weather

logger = logging.getLogger("lomportbot.generating_a_reply_message")


async def generating_a_reply_message(point) -> str:
    yand_navi_url = hlink(
        " В путь с Яндекс Навигатором! ",
        f"https://yandex.ru/navi?whatshere%5Bpoint%5D={point[3]}%2C{point[2]}&whatshere%5Bzoom%5D=16.768925&ll={point[3]}%2C{point[2]}&z=16.768925&si=e5wmhgefmj352468jpym3ewa4m",
    )
    yand_map_url = hlink(
        " В путь с Яндекс Картами! ",
        f"https://yandex.ru/maps?whatshere%5Bpoint%5D={point[3]}%2C{point[2]}&whatshere%5Bzoom%5D=16.0&ll={point[3]}%2C{point[2]}&z=16.0&si=e5wmhgefmj352468jpym3ewa4m",
    )
    two_gis_url = hlink(
        " В путь с 2GIS! ", f"https://2gis.ru/geo/{point[3]},{point[2]}"
    )
    weather = await get_weather(point[2], point[3])

    if point[4]:
        phone_number = point[4]
    else:
        phone_number = "Неизвестен"

    if weather:
        final_weather_data = weather["current"]["temperature_2m"]
    else:
        final_weather_data = "Ошибка загрузки погоды!"

    reply_message = f"""Запрашиваемый пункт: {point[1]}
                 \nАдрес: {point[0]}
                 \n{yand_navi_url}
                 \n{yand_map_url}
                 \n{two_gis_url}
                 \nНомер телефона: {phone_number}
                 \nПогода в районе ПЗУ😄: температура воздуха : {final_weather_data}"""

    return reply_message
