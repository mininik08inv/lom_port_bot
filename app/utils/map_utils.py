"""
Утилиты для работы с картами и ссылками
"""

from typing import List, Dict
from urllib.parse import quote


def generate_yandex_map_link(lat: float, lon: float, name: str) -> str:
    """
    Создает ссылку на Яндекс.Карты с меткой
    
    Args:
        lat: Широта
        lon: Долгота  
        name: Название точки
        
    Returns:
        URL ссылка на Яндекс.Карты
    """
    encoded_name = quote(name)
    return f"https://yandex.ru/maps/?pt={lon},{lat}&z=15&l=map&text={encoded_name}"


def generate_google_map_link(lat: float, lon: float, name: str = "") -> str:
    """
    Создает ссылку на Google Maps
    
    Args:
        lat: Широта
        lon: Долгота
        name: Название точки (опционально)
        
    Returns:
        URL ссылка на Google Maps
    """
    if name:
        encoded_name = quote(name)
        return f"https://maps.google.com/?q={lat},{lon}+({encoded_name})"
    else:
        return f"https://maps.google.com/?q={lat},{lon}"


def generate_2gis_map_link(lat: float, lon: float, name: str = "") -> str:
    """
    Создает ссылку на 2ГИС
    
    Args:
        lat: Широта
        lon: Долгота
        name: Название точки (опционально)
        
    Returns:
        URL ссылка на 2ГИС
    """
    return f"https://2gis.ru/geo/{lon},{lat}"


def get_region_name(region_code: str) -> str:
    """
    Возвращает название региона по коду
    
    Args:
        region_code: Код региона (например, "69", "68")
        
    Returns:
        Название региона или код, если название не найдено
    """
    region_codes = {
        '69': 'Тверская область',
        '68': 'Тамбовская область', 
        '62': 'Рязанская область',
        '35': 'Вологодская область',
        '77': 'Москва',
        '78': 'Санкт-Петербург',
        '23': 'Краснодарский край',
        '52': 'Нижегородская область',
        '47': 'Ленинградская область',
        '50': 'Московская область',
        '51': 'Мурманская область',
        '53': 'Новгородская область',
        '54': 'Новосибирская область',
        '55': 'Омская область',
        '56': 'Оренбургская область',
        '57': 'Орловская область',
        '58': 'Пензенская область',
        '59': 'Пермский край',
        '60': 'Псковская область',
        '61': 'Ростовская область',
        '63': 'Самарская область',
        '64': 'Саратовская область',
        '65': 'Сахалинская область',
        '66': 'Свердловская область',
        '67': 'Смоленская область',
        '70': 'Томская область',
        '71': 'Тульская область',
        '72': 'Тюменская область',
        '73': 'Ульяновская область',
        '74': 'Челябинская область',
        '75': 'Забайкальский край',
        '76': 'Ярославская область',
        '79': 'Еврейская автономная область',
        '80': 'Забайкальский край',
        '81': 'Пермский край',
        '82': 'Крым',
        '83': 'Ненецкий автономный округ',
        '84': 'Ханты-Мансийский автономный округ',
        '85': 'Чукотский автономный округ',
        '86': 'Ямало-Ненецкий автономный округ'
    }
    
    return region_codes.get(region_code, f'Регион {region_code}')


def generate_weight_control_warning(weight_controls: List[Dict]) -> str:
    """
    Генерирует текст предупреждения о пунктах весового контроля
    
    Args:
        weight_controls: Список найденных пунктов весового контроля
        
    Returns:
        Форматированный текст предупреждения
    """
    if not weight_controls:
        return ""
    
    count = len(weight_controls)
    
    if count == 1:
        wc = weight_controls[0]
        distance = round(wc['distance'], 1)
        region_info = f" ({wc['region']} регион)" if wc.get('region') else ""
        
        warning = f"🚨 ВНИМАНИЕ! В {distance} км найден пункт весового контроля:\n"
        warning += f"📍 {wc['name']}{region_info}"
        
        if wc.get('district'):
            warning += f"\n🏘️ {wc['district']}"
            
        if wc.get('description'):
            desc = wc['description'][:100] + "..." if len(wc['description']) > 100 else wc['description']
            warning += f"\n📝 {desc}"
            
        return warning
    
    else:
        nearest = min(weight_controls, key=lambda x: x['distance'])
        nearest_distance = round(nearest['distance'], 1)
        
        warning = f"🚨 ВНИМАНИЕ! Найдено {count} пунктов весового контроля в радиусе 50 км\n"
        warning += f"📍 Ближайший: {nearest['name']} ({nearest_distance} км)"
        
        if nearest.get('region'):
            region_name = get_region_name(nearest['region'])
            warning += f" - {region_name}"
            
        # Показываем еще несколько ближайших
        if count > 1:
            warning += "\n\n🔍 Другие пункты:"
            for wc in weight_controls[1:4]:  # Показываем до 3 дополнительных
                distance = round(wc['distance'], 1)
                region_info = ""
                if wc.get('region'):
                    region_name = get_region_name(wc['region'])
                    region_info = f" - {region_name}"
                warning += f"\n• {wc['name'][:40]}... ({distance} км){region_info}"
                
        if count > 4:
            warning += f"\n• ... и еще {count - 4} пунктов"
            
        return warning


def generate_distance_info(distance: float) -> str:
    """
    Генерирует красивое отображение расстояния с эмодзи
    
    Args:
        distance: Расстояние в километрах
        
    Returns:
        Форматированная строка с расстоянием
    """
    distance_rounded = round(distance, 1)
    
    if distance_rounded < 5:
        emoji = "🔴"  # Очень близко
    elif distance_rounded < 15:
        emoji = "🟡"  # Близко
    elif distance_rounded < 30:
        emoji = "🟠"  # Средне
    else:
        emoji = "🟢"  # Далеко
        
    return f"{emoji} {distance_rounded} км"


def format_weight_control_info(wc: Dict) -> str:
    """
    Форматирует информацию о пункте весового контроля для отображения
    
    Args:
        wc: Словарь с данными о пункте весового контроля
        
    Returns:
        Форматированная строка с информацией
    """
    info = f"📍 {wc['name']}\n"
    
    if wc.get('distance') is not None:
        info += f"📏 Расстояние: {generate_distance_info(wc['distance'])}\n"
    
    if wc.get('region'):
        info += f"🗺️ Регион: {wc['region']}\n"
        
    if wc.get('district'):
        info += f"🏘️ Район: {wc['district']}\n"
        
    if wc.get('address'):
        info += f"🏠 Адрес: {wc['address']}\n"
        
    if wc.get('description'):
        desc = wc['description'][:150] + "..." if len(wc['description']) > 150 else wc['description']
        info += f"📝 Описание: {desc}\n"
        
    return info.strip()


def create_map_links_text(wc: Dict) -> str:
    """
    Создает текст со ссылками на разные карты
    
    Args:
        wc: Словарь с данными о пункте весового контроля
        
    Returns:
        Текст со ссылками на карты
    """
    if not wc.get('latitude') or not wc.get('longitude'):
        return "Координаты недоступны"
    
    lat, lon = wc['latitude'], wc['longitude']
    name = wc['name']
    
    yandex_link = generate_yandex_map_link(lat, lon, name)
    google_link = generate_google_map_link(lat, lon, name)
    gis_2_link = generate_2gis_map_link(lat, lon, name)
    
    links_text = "🗺️ Открыть на картах:\n"
    links_text += f"• [Яндекс.Карты]({yandex_link})\n"
    links_text += f"• [Google Maps]({google_link})\n"
    links_text += f"• [2ГИС]({gis_2_link})"
    
    return links_text
