"""
Модуль для работы с JSON данными
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Union, Optional
from config import JSON_FILES, DEFAULT_BALANCE

logger = logging.getLogger(__name__)

class DataManager:
    """Класс для управления JSON файлами"""
    
    @staticmethod
    def load_json(filename: str) -> Union[Dict, List]:
        """Загрузка данных из JSON файла"""
        try:
            if not os.path.exists(filename):
                logger.warning(f"Файл {filename} не существует, возвращаем пустую структуру")
                return {}
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Успешно загружены данные из {filename}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON в {filename}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Ошибка загрузки файла {filename}: {e}")
            return {}

    @staticmethod
    def save_json(filename: str, data: Union[Dict, List]) -> bool:
        """Сохранение данных в JSON файл"""
        try:
            # Создаем директорию если не существует
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"Данные успешно сохранены в {filename}")
                return True
        except Exception as e:
            logger.error(f"Ошибка сохранения файла {filename}: {e}")
            return False

    @staticmethod
    def get_next_id(data_list: List[Dict]) -> int:
        """Получить следующий доступный ID"""
        if not data_list:
            return 1
        return max(item.get('id', 0) for item in data_list) + 1

    @staticmethod
    def init_data_files():
        """Инициализация файлов данных при первом запуске"""
        try:
            # Создаем директорию data если не существует
            os.makedirs('data', exist_ok=True)
            
            # Инициализируем файлы с базовыми данными если они не существуют
            DataManager._init_draws_file()
            DataManager._init_tickets_file()
            DataManager._init_balance_file()
            DataManager._init_banners_file()
            DataManager._init_packages_file()
            
        except Exception as e:
            logger.error(f"Ошибка инициализации данных: {e}")

    @staticmethod
    def _init_draws_file():
        """Инициализация файла розыгрышей"""
        if not os.path.exists(JSON_FILES['draws']):
            initial_draws = {
                "draws": [
                    {
                        "id": 1,
                        "title": "Большое Лото #1",
                        "type": "big",
                        "date": "2025-08-15",
                        "time": "20:00",
                        "cost": 50,
                        "prize": 1000000,
                        "completed": False,
                        "numbers": [],
                        "time_left": "2 дня 12 часов",
                        "numbers_count": 8,
                        "button_text": "Участвовать!",
                        "currency": "COINS",
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "title": "Экспресс Лото #1",
                        "type": "express",
                        "date": "2025-08-15",
                        "time": "12:00",
                        "cost": 20,
                        "prize": 500000,
                        "completed": False,
                        "numbers": [],
                        "time_left": "12 часов",
                        "numbers_count": 6,
                        "button_text": "Участвовать!",
                        "currency": "COINS",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            DataManager.save_json(JSON_FILES['draws'], initial_draws)
            logger.info("Инициализированы данные розыгрышей")

    @staticmethod
    def _init_tickets_file():
        """Инициализация файла билетов"""
        if not os.path.exists(JSON_FILES['tickets']):
            initial_tickets = {"tickets": []}
            DataManager.save_json(JSON_FILES['tickets'], initial_tickets)
            logger.info("Инициализирован файл билетов")

    @staticmethod
    def _init_balance_file():
        """Инициализация файла баланса"""
        if not os.path.exists(JSON_FILES['balance']):
            initial_balance = {"balance": DEFAULT_BALANCE}
            DataManager.save_json(JSON_FILES['balance'], initial_balance)
            logger.info(f"Инициализирован баланс пользователя: {DEFAULT_BALANCE}")
        else:
            # Проверяем текущий баланс и устанавливаем минимальный если он 0
            current_balance_data = DataManager.load_json(JSON_FILES['balance'])
            current_balance = current_balance_data.get('balance', 0) if isinstance(current_balance_data, dict) else 0
            if current_balance <= 0:
                initial_balance = {"balance": DEFAULT_BALANCE}
                DataManager.save_json(JSON_FILES['balance'], initial_balance)
                logger.info(f"Баланс был 0, установлен начальный баланс: {DEFAULT_BALANCE}")

    @staticmethod
    def _init_banners_file():
        """Инициализация файла баннеров"""
        if not os.path.exists(JSON_FILES['banners']):
            initial_banners = {
                "banners": [
                    {
                        "id": 1,
                        "title": "Джекпот 1 миллион!",
                        "subtitle": "Участвуйте в Большом Лото",
                        "image": "banner1.jpg",
                        "active": True
                    },
                    {
                        "id": 2,
                        "title": "Быстрые выигрыши",
                        "subtitle": "Экспресс Лото каждый день",
                        "image": "banner2.jpg",
                        "active": True
                    }
                ]
            }
            DataManager.save_json(JSON_FILES['banners'], initial_banners)
            logger.info("Инициализированы баннеры")

    @staticmethod
    def _init_packages_file():
        """Инициализация файла пакетов"""
        if not os.path.exists(JSON_FILES['packages']):
            initial_packages = {
                "packages": [
                    {
                        "id": 1,
                        "name": "VIP пакет",
                        "category": "big",
                        "price": 200,
                        "currency": "COINS",
                        "created_date": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "name": "Экспресс набор",
                        "category": "express",
                        "price": 100,
                        "currency": "COINS",
                        "created_date": datetime.now().isoformat()
                    },
                    {
                        "id": 3,
                        "name": "Универсальный пакет",
                        "category": "all",
                        "price": 250,
                        "currency": "COINS",
                        "created_date": datetime.now().isoformat()
                    }
                ]
            }
            DataManager.save_json(JSON_FILES['packages'], initial_packages)
            logger.info("Инициализированы пакеты")