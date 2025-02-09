import requests
from aiogram.utils.markdown import hlink


def generating_a_reply_message(point: tuple) -> str:
    yand_navi_url = hlink(' В путь с Яндекс Навигатором! ',
                          f'https://yandex.ru/navi?whatshere%5Bpoint%5D={point[4]}%2C{point[3]}&whatshere%5Bzoom%5D=16.768925&ll={point[4]}%2C{point[3]}&z=16.768925&si=e5wmhgefmj352468jpym3ewa4m')
    yand_map_url = hlink(' В путь с Яндекс Картами! ',
                         f'https://yandex.ru/maps?whatshere%5Bpoint%5D={point[4]}%2C{point[3]}&whatshere%5Bzoom%5D=16.0&ll={point[4]}%2C{point[3]}&z=16.0&si=e5wmhgefmj352468jpym3ewa4m')
    two_gis_url = hlink(' В путь с 2GIS! ', f'https://2gis.ru/geo/{point[4]},{point[3]}')

    weather = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={point[3]}&longitude={point[4]}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    phone_number = point[-3] if len(point[-3]) > 0 else 'Неизвестен'

    reply_message = f'''Запрашиваемый пункт: {point[2]}
                 \nАдрес: {point[1]}
                 \n{yand_navi_url}
                 \n{yand_map_url}
                 \n{two_gis_url}
                 \nНомер телефона: {phone_number}
                 \nПогода в районе погрузки😄: температура воздуха : {weather.json()['current']['temperature_2m']}'''

    return reply_message
