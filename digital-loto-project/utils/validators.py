"""
Модуль валидации данных
"""
from typing import List
from config import MAX_LOTTERY_NUMBER

class Validators:
    """Класс для валидации данных лотереи"""
    
    @staticmethod
    def validate_ticket_numbers(numbers: List[int], draw_type: str) -> bool:
        """Валидация чисел билета"""
        required_count = 8 if draw_type == 'big' else 6
        
        # Проверяем количество чисел
        if len(numbers) != required_count:
            return False
        
        # Проверяем диапазон чисел
        if not all(1 <= num <= MAX_LOTTERY_NUMBER for num in numbers):
            return False
        
        # Проверяем на дубликаты
        if len(set(numbers)) != len(numbers):
            return False
        
        return True
    
    @staticmethod
    def validate_balance(balance: float) -> bool:
        """Валидация баланса"""
        return isinstance(balance, (int, float)) and balance >= 0
    
    @staticmethod
    def validate_draw_data(data: dict) -> bool:
        """Валидация данных розыгрыша"""
        required_fields = ['title', 'category', 'cost']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_package_data(data: dict) -> bool:
        """Валидация данных пакета"""
        required_fields = ['name', 'category', 'price']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def validate_package_type(package_type: str) -> bool:
        """Валидация типа пакета"""
        valid_types = ['all', 'big_only', 'express_only']
        return package_type in valid_types