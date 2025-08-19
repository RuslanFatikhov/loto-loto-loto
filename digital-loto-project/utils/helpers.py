"""
Вспомогательные функции для приложения лотереи
"""
import random
import logging
from datetime import datetime
from typing import List, Dict
from config import MAX_LOTTERY_NUMBER, PRIZE_TABLE

logger = logging.getLogger(__name__)

class LotteryHelpers:
    """Класс с вспомогательными функциями для лотереи"""
    
    @staticmethod
    def generate_random_numbers(count: int, max_number: int = MAX_LOTTERY_NUMBER) -> List[int]:
        """Генерация случайных чисел для розыгрыша"""
        try:
            numbers = random.sample(range(1, max_number + 1), count)
            numbers.sort()
            logger.info(f"Сгенерированы числа: {numbers}")
            return numbers
        except Exception as e:
            logger.error(f"Ошибка генерации случайных чисел: {e}")
            return []

    @staticmethod
    def check_winning_ticket(ticket_numbers: List[int], draw_numbers: List[int]) -> int:
        """Проверка выигрышного билета - возвращает количество совпадений"""
        try:
            matches = len(set(ticket_numbers) & set(draw_numbers))
            logger.info(f"Найдено {matches} совпадений")
            return matches
        except Exception as e:
            logger.error(f"Ошибка проверки билета: {e}")
            return 0

    @staticmethod
    def calculate_prize(matches: int, draw_type: str) -> float:
        """Вычисление размера приза на основе количества совпадений"""
        return PRIZE_TABLE.get(draw_type, {}).get(matches, 0)

    @staticmethod
    def format_ticket_time(time_string: str) -> str:
        """Форматирование времени покупки"""
        if not time_string:
            return "Не указано"
        
        try:
            if 'T' in time_string:
                date_obj = datetime.fromisoformat(time_string.replace('Z', '+00:00'))
                return date_obj.strftime('%d.%m.%Y %H:%M')
            return time_string
        except:
            return time_string

    @staticmethod
    def get_ticket_status_text(status: str) -> str:
        """Текстовое описание статуса билета"""
        status_map = {
            'pending': 'Ждет выбора чисел',
            'confirmed': 'Ждет розыгрыша', 
            'completed': 'Розыгрыш завершен',
            'winning': 'Выигрышный!'
        }
        return status_map.get(status, 'Неизвестно')

    @staticmethod
    def get_draw_status_text(draw: Dict) -> str:
        """Текстовое описание статуса розыгрыша"""
        if draw.get('completed', False):
            return "Завершен"
        else:
            return f"Активный до {draw.get('time', '')}"

    @staticmethod
    def determine_ticket_status(ticket: Dict, draw: Dict) -> str:
        """Определение статуса билета"""
        numbers = ticket.get('numbers', [])
        
        if len(numbers) == 0:
            return 'pending'
        
        if not draw.get('completed', False):
            return 'confirmed'
        
        if draw.get('numbers') and LotteryHelpers.check_winning_ticket(numbers, draw['numbers']) > 0:
            return 'winning'
        
        return 'completed'

    @staticmethod
    def enrich_ticket_data(ticket: Dict, draw: Dict) -> Dict:
        """Обогащение данных билета"""
        enriched = ticket.copy()
        
        enriched['formatted_time'] = LotteryHelpers.format_ticket_time(ticket.get('created_at', ''))
        
        status = LotteryHelpers.determine_ticket_status(ticket, draw)
        enriched['status'] = status
        enriched['status_text'] = LotteryHelpers.get_ticket_status_text(status)
        
        numbers = ticket.get('numbers', [])
        enriched['is_pending'] = len(numbers) == 0
        
        return enriched

class TicketGrouping:
    """Класс для группировки и фильтрации билетов"""
    
    @staticmethod
    def group_tickets_by_draw(tickets: List[Dict], draws: List[Dict]) -> List[Dict]:
        """Группировка билетов по розыгрышам"""
        draws_dict = {draw['id']: draw for draw in draws}
        grouped = {}
        
        for ticket in tickets:
            draw_id = ticket.get('draw_id')
            if draw_id not in grouped:
                draw_info = draws_dict.get(draw_id, {
                    'id': draw_id,
                    'title': f'Розыгрыш #{draw_id}',
                    'type': 'big',
                    'completed': False
                })
                grouped[draw_id] = {
                    'draw': draw_info,
                    'tickets': []
                }
            
            enriched_ticket = LotteryHelpers.enrich_ticket_data(ticket, draws_dict.get(draw_id, {}))
            grouped[draw_id]['tickets'].append(enriched_ticket)
        
        # Преобразуем в список для шаблона
        result = []
        for draw_id, group in grouped.items():
            draw = group['draw']
            tickets_list = sorted(group['tickets'], key=lambda x: x.get('created_at', ''), reverse=True)
            
            result.append({
                'draw_id': draw_id,
                'draw_title': draw.get('title', f'Розыгрыш #{draw_id}'),
                'draw_image': f'https://via.placeholder.com/50/667eea/white?text={draw_id}',
                'draw_status': LotteryHelpers.get_draw_status_text(draw),
                'tickets_count': len(tickets_list),
                'tickets': tickets_list
            })
        
        return result

    @staticmethod
    def get_draws_for_filter(tickets: List[Dict], draws: List[Dict]) -> List[Dict]:
        """Получить розыгрыши для фильтра"""
        draws_dict = {draw['id']: draw for draw in draws}
        ticket_draw_ids = set(ticket.get('draw_id') for ticket in tickets)
        
        filters = []
        for draw_id in ticket_draw_ids:
            if draw_id in draws_dict:
                draw = draws_dict[draw_id]
                filters.append({
                    'id': draw_id,
                    'title': draw.get('title', f'Розыгрыш #{draw_id}'),
                    'image': f'https://via.placeholder.com/50/667eea/white?text={draw_id}'
                })
        
        return filters

    @staticmethod
    def apply_ticket_filters(tickets: List[Dict], draws: List[Dict], status: str, draw_id: str) -> List[Dict]:
        """Применение фильтров к билетам"""
        filtered = tickets
        
        # Фильтр по розыгрышу
        if draw_id != 'all':
            try:
                draw_id_int = int(draw_id)
                filtered = [t for t in filtered if t.get('draw_id') == draw_id_int]
            except (ValueError, TypeError):
                pass
        
        # Обогащаем данные
        draws_dict = {draw['id']: draw for draw in draws}
        enriched_tickets = []
        
        for ticket in filtered:
            draw = draws_dict.get(ticket.get('draw_id'), {})
            enriched = LotteryHelpers.enrich_ticket_data(ticket, draw)
            enriched_tickets.append(enriched)
        
        # Фильтр по статусу
        if status != 'all':
            enriched_tickets = [t for t in enriched_tickets if t.get('status') == status]
        
        return enriched_tickets