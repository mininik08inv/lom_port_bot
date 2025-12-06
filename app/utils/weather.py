import aiohttp
import logging

logger = logging.getLogger(__name__)


async def get_weather(lat, lon):
    url = f"http://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=3) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Weather API error(Ошибка получения погоды): {str(e)}", exc_info=True)
            return None
