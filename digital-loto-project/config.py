"""
Конфигурация приложения лотереи
"""
import os
import logging

# Настройка Flask
SECRET_KEY = 'your-secret-key-here'
DEBUG = True
HOST = '0.0.0.0'
PORT = 5700

# Пути к JSON файлам
JSON_FILES = {
    'draws': 'static/data/draws.json',
    'tickets': 'data/tickets.json',
    'balance': 'data/balance.json',
    'banners': 'data/banners.json',
    'packages': 'data/packages.json'
}

# Цены билетов
TICKET_PRICES = {
    'big': 10,
    'express': 5
}

# Цены пакетов
PACKAGE_PRICES = {
    'all': 50,
    'big_only': 30,
    'express_only': 20
}

# Таблица призов
PRIZE_TABLE = {
    'big': {8: 1000000, 7: 50000, 6: 5000, 5: 500, 4: 50},
    'express': {6: 500000, 5: 25000, 4: 2500, 3: 250}
}

# Настройка логирования
def setup_logging():
    """Настройка системы логирования"""
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# Начальный баланс пользователя
DEFAULT_BALANCE = 1500.0

# Максимальное число в лотерее
MAX_LOTTERY_NUMBER = 36