"""
Сервис для работы с данными пунктов весового контроля
"""

import json
import math
from typing import List, Dict
from app.database.db import get_db_connection
import logging

logger = logging.getLogger("lomportbot.weight_control_service")


class WeightControlService:
    """Сервис для работы с пунктами весового контроля"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Вычисляет расстояние между двумя точками на Земле в километрах
        Использует формулу гаверсинуса
        """
        # Радиус Земли в километрах
        R = 6371.0
        
        # Преобразуем градусы в радианы
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Разности координат
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Формула гаверсинуса
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        # Расстояние в километрах
        distance = R * c
        return distance
    
    @staticmethod
    async def find_nearby_weight_control(
        pzu_lat: float, 
        pzu_lon: float, 
        radius_km: int = 50
    ) -> List[Dict]:
        """
        Находит пункты весового контроля в заданном радиусе от ПЗУ
        
        Args:
            pzu_lat: Широта ПЗУ
            pzu_lon: Долгота ПЗУ  
            radius_km: Радиус поиска в километрах
            
        Returns:
            Список словарей с данными о пунктах весового контроля
        """
        try:
            conn = await get_db_connection()
            
            # Приблизительные границы для оптимизации запроса
            # 1 градус ≈ 111 км
            lat_delta = radius_km / 111.0
            lon_delta = radius_km / (111.0 * math.cos(math.radians(pzu_lat)))
            
            # Запрос с предварительной фильтрацией по квадрату
            query = """
                SELECT name, region, latitude, longitude, address, description
                FROM weight_control_points 
                WHERE latitude IS NOT NULL 
                  AND longitude IS NOT NULL
                  AND latitude BETWEEN $1 AND $2
                  AND longitude BETWEEN $3 AND $4
            """
            
            results = await conn.fetch(
                query,
                pzu_lat - lat_delta,
                pzu_lat + lat_delta, 
                pzu_lon - lon_delta,
                pzu_lon + lon_delta
            )
            
            await conn.close()
            
            # Точная фильтрация по расстоянию
            nearby_points = []
            for row in results:
                distance = WeightControlService.haversine_distance(
                    pzu_lat, pzu_lon,
                    float(row['latitude']), float(row['longitude'])
                )
                
                if distance <= radius_km:
                    point_data = {
                        'name': row['name'],
                        'region': row['region'],
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'address': row['address'],
                        'description': row['description'],
                        'distance': distance
                    }
                    nearby_points.append(point_data)
            
            # Сортируем по расстоянию
            nearby_points.sort(key=lambda x: x['distance'])
            
            logger.info(f"Найдено {len(nearby_points)} пунктов весового контроля "
                       f"в радиусе {radius_km} км от координат {pzu_lat}, {pzu_lon}")
            
            return nearby_points
            
        except Exception as e:
            logger.error(f"Ошибка при поиске пунктов весового контроля: {e}")
            return []
    

