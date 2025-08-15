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
                SELECT external_id, name, region, district, latitude, longitude, 
                       address, description, url
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
                        'external_id': row['external_id'],
                        'name': row['name'],
                        'region': row['region'],
                        'district': row['district'],
                        'latitude': float(row['latitude']),
                        'longitude': float(row['longitude']),
                        'address': row['address'],
                        'description': row['description'],
                        'url': row['url'],
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
    
    @staticmethod
    async def load_weight_control_data(json_file_path: str) -> bool:
        """
        Загружает данные о пунктах весового контроля из JSON файла в базу данных
        
        Args:
            json_file_path: Путь к JSON файлу с данными
            
        Returns:
            True если загрузка прошла успешно, False в случае ошибки
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Загружаем {len(data)} пунктов весового контроля из {json_file_path}")
            
            conn = await get_db_connection()
            
            # Создаем таблицу если её нет
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS weight_control_points (
                    id SERIAL PRIMARY KEY,
                    external_id VARCHAR(50) UNIQUE,
                    name TEXT NOT NULL,
                    region VARCHAR(10),
                    district VARCHAR(100),
                    latitude DECIMAL(10,8),
                    longitude DECIMAL(11,8),
                    address TEXT,
                    description TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Создаем индекс для быстрого поиска по координатам
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_weight_control_coords 
                ON weight_control_points (latitude, longitude);
            """)
            
            loaded_count = 0
            skipped_count = 0
            
            for point in data:
                try:
                    # Загружаем только пункты с координатами
                    if point.get('coordinates') and point['coordinates']:
                        await conn.execute("""
                            INSERT INTO weight_control_points 
                            (external_id, name, region, district, latitude, longitude, 
                             address, description, url)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                            ON CONFLICT (external_id) DO UPDATE SET
                                name = EXCLUDED.name,
                                region = EXCLUDED.region,
                                district = EXCLUDED.district,
                                latitude = EXCLUDED.latitude,
                                longitude = EXCLUDED.longitude,
                                address = EXCLUDED.address,
                                description = EXCLUDED.description,
                                url = EXCLUDED.url,
                                updated_at = NOW()
                        """, 
                        point['id'], 
                        point['name'], 
                        point.get('region', ''), 
                        point.get('district', ''),
                        point['coordinates']['lat'], 
                        point['coordinates']['lng'],
                        point.get('address', ''), 
                        point.get('description', ''), 
                        point.get('url', ''))
                        
                        loaded_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    logger.error(f"Ошибка при загрузке пункта {point.get('id', 'unknown')}: {e}")
                    skipped_count += 1
            
            await conn.close()
            
            logger.info(f"Загрузка завершена: {loaded_count} загружено, {skipped_count} пропущено")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных весового контроля: {e}")
            return False
    
    @staticmethod
    async def get_stats() -> Dict:
        """
        Получает статистику по пунктам весового контроля в базе данных
        
        Returns:
            Словарь со статистикой
        """
        try:
            conn = await get_db_connection()
            
            # Общее количество
            total_count = await conn.fetchval(
                "SELECT COUNT(*) FROM weight_control_points"
            )
            
            # Количество с координатами
            with_coords_count = await conn.fetchval(
                "SELECT COUNT(*) FROM weight_control_points WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
            )
            
            # Количество по регионам
            regions_stats = await conn.fetch(
                "SELECT region, COUNT(*) as count FROM weight_control_points WHERE region != '' GROUP BY region ORDER BY count DESC LIMIT 10"
            )
            
            await conn.close()
            
            return {
                'total_points': total_count,
                'points_with_coordinates': with_coords_count,
                'top_regions': [{'region': r['region'], 'count': r['count']} for r in regions_stats]
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return {
                'total_points': 0,
                'points_with_coordinates': 0,
                'top_regions': []
            }
