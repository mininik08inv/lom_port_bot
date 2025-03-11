import requests
from aiogram.utils.markdown import hlink

import logging

logger = logging.getLogger('lomportbot.generating_a_reply_message')


def generating_a_reply_message(point: tuple) -> str:
    yand_navi_url = hlink(' В путь с Яндекс Навигатором! ',
                          f'https://yandex.ru/navi?whatshere%5Bpoint%5D={point[3]}%2C{point[2]}&whatshere%5Bzoom%5D=16.768925&ll={point[3]}%2C{point[2]}&z=16.768925&si=e5wmhgefmj352468jpym3ewa4m')
    yand_map_url = hlink(' В путь с Яндекс Картами! ',
                         f'https://yandex.ru/maps?whatshere%5Bpoint%5D={point[3]}%2C{point[2]}&whatshere%5Bzoom%5D=16.0&ll={point[3]}%2C{point[2]}&z=16.0&si=e5wmhgefmj352468jpym3ewa4m')
    two_gis_url = hlink(' В путь с 2GIS! ', f'https://2gis.ru/geo/{point[3]},{point[2]}')
    try:
        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={point[2]}&longitude={point[3]}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    except Exception as e:
        weather = False
        logger.exception("Ошибка в получении погоды", e)


    if point[4]:
        phone_number = point[4]
    else:
        phone_number = 'Неизвестен'

    if weather:
        final_weather_data = weather.json()['current']['temperature_2m']
    else:
        final_weather_data = 'Ошибка загрузки погоды!'

    reply_message = f'''Запрашиваемый пункт: {point[1]}
                 \nАдрес: {point[0]}
                 \n{yand_navi_url}
                 \n{yand_map_url}
                 \n{two_gis_url}
                 \nНомер телефона: {phone_number}
                 \nПогода в районе ПЗУ😄: температура воздуха : {final_weather_data}'''

    return reply_message
