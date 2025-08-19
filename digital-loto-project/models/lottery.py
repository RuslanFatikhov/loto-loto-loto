"""
Основная бизнес-логика лотереи
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from models.data_manager import DataManager
from utils.helpers import LotteryHelpers
from utils.validators import Validators
from config import JSON_FILES, TICKET_PRICES, PACKAGE_PRICES

logger = logging.getLogger(__name__)

class LotteryService:
    """Сервис для работы с лотереей"""
    
    def __init__(self):
        self.data_manager = DataManager()
    
    # ========= РАБОТА С РОЗЫГРЫШАМИ =========
    
    def get_all_draws(self) -> List[Dict]:
        """Получить все розыгрыши"""
        draws_data = self.data_manager.load_json(JSON_FILES['draws'])
        return draws_data.get('draws', []) if isinstance(draws_data, dict) else []

    def get_draw_by_id(self, draw_id):

        try:
            draws_data = self.data_manager.load_json(JSON_FILES['draws'])
            
            # Обрабатываем разные форматы данных
            if isinstance(draws_data, dict) and 'draws' in draws_data:
                draws = draws_data['draws']
            elif isinstance(draws_data, list):
                draws = draws_data  # Ваш случай
            else:
                logger.warning(f"Неожиданный формат данных: {type(draws_data)}")
                return None
                
            for draw in draws:
                if draw['id'] == draw_id:
                    logger.info(f"Найден розыгрыш с ID {draw_id}")
                    return draw
            
            logger.warning(f"Розыгрыш с ID {draw_id} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения розыгрыша {draw_id}: {e}")
            return None    

    def get_all_draws(self):
        """Получить все розыгрыши"""
        try:
            draws_data = self.data_manager.load_json(JSON_FILES['draws'])
            
            # Обрабатываем разные форматы данных
            if isinstance(draws_data, dict) and 'draws' in draws_data:
                return draws_data['draws']
            elif isinstance(draws_data, list):
                return draws_data  # Ваш случай
            else:
                logger.warning(f"Неожиданный формат данных: {type(draws_data)}")
                return []
        except Exception as e:
            logger.error(f"Ошибка получения розыгрышей: {e}")
            return []

    def add_draw(self, draw_data: Dict) -> Optional[Dict]:
        """Добавить новый розыгрыш"""
        try:
            if not Validators.validate_draw_data(draw_data):
                return None
            
            draws_data = self.data_manager.load_json(JSON_FILES['draws'])
            if 'draws' not in draws_data:
                draws_data['draws'] = []
            
            next_id = self.data_manager.get_next_id(draws_data['draws'])
            
            new_draw = {
                'id': next_id,
                'title': draw_data['title'],
                'type': draw_data['category'],  # category -> type для совместимости
                'cost': int(draw_data['cost']),
                'image': draw_data.get('image', ''),
                'bg': draw_data.get('bg', ''),
                'time_left': draw_data.get('time_left', ''),
                'numbers_count': int(draw_data.get('numbers_count', 6)),
                'button_text': draw_data.get('button_text', 'Участвовать!'),
                'completed': False,
                'numbers': [],
                'tickets_count': 0,
                'currency': 'COINS',
                'created_at': datetime.now().isoformat()
            }
            
            # Добавляем поля date и time для совместимости
            if draw_data.get('time_left'):
                new_draw['date'] = datetime.now().strftime('%Y-%m-%d')
                new_draw['time'] = '20:00'
            
            draws_data['draws'].append(new_draw)
            
            if self.data_manager.save_json(JSON_FILES['draws'], draws_data):
                logger.info(f"Новый розыгрыш {next_id} добавлен")
                return new_draw
            
            return None
        except Exception as e:
            logger.error(f"Ошибка добавления розыгрыша: {e}")
            return None
    
    def update_draw(self, draw_id: int, draw_data: Dict) -> Optional[Dict]:
        """Обновить розыгрыш"""
        try:
            draws_data = self.data_manager.load_json(JSON_FILES['draws'])
            draws = draws_data.get('draws', [])
            
            draw_index = -1
            for i, draw in enumerate(draws):
                if draw['id'] == draw_id:
                    draw_index = i
                    break
            
            if draw_index == -1:
                return None
            
            # Обновляем поля
            updatable_fields = {
                'title': 'title',
                'category': 'type',  # category -> type
                'cost': 'cost',
                'image': 'image',
                'bg': 'bg',
                'time_left': 'time_left',
                'numbers_count': 'numbers_count',
                'button_text': 'button_text'
            }
            
            for api_field, db_field in updatable_fields.items():
                if api_field in draw_data:
                    if api_field in ['cost', 'numbers_count']:
                        draws[draw_index][db_field] = int(draw_data[api_field])
                    else:
                        draws[draw_index][db_field] = draw_data[api_field]
            
            draws[draw_index]['updated_at'] = datetime.now().isoformat()
            
            if self.data_manager.save_json(JSON_FILES['draws'], draws_data):
                logger.info(f"Розыгрыш {draw_id} обновлен")
                return draws[draw_index]
            
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления розыгрыша {draw_id}: {e}")
            return None
    
    def delete_draw(self, draw_id: int) -> bool:
        """Удалить розыгрыш"""
        try:
            # Проверяем, есть ли билеты на этот розыгрыш
            user_tickets = self.get_user_tickets(draw_id)
            if user_tickets:
                return False
            
            draws_data = self.data_manager.load_json(JSON_FILES['draws'])
            draws = draws_data.get('draws', [])
            
            # Находим розыгрыш для удаления
            new_draws = [draw for draw in draws if draw['id'] != draw_id]
            
            if len(new_draws) == len(draws):  # Розыгрыш не найден
                return False
            
            draws_data['draws'] = new_draws
            
            if self.data_manager.save_json(JSON_FILES['draws'], draws_data):
                logger.info(f"Розыгрыш {draw_id} удален")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления розыгрыша {draw_id}: {e}")
            return False
    
    def conduct_draw(self, draw_id: int) -> Optional[Dict]:
        """Провести розыгрыш"""
        try:
            draws_data = self.data_manager.load_json(JSON_FILES['draws'])
            draws = draws_data.get('draws', [])
            
            draw_index = -1
            target_draw = None
            
            for i, draw in enumerate(draws):
                if draw['id'] == draw_id:
                    draw_index = i
                    target_draw = draw
                    break
            
            if not target_draw or target_draw.get('completed', False):
                return None
            
            # Генерируем выигрышные числа
            number_count = 8 if target_draw['type'] == 'big' else 6
            winning_numbers = LotteryHelpers.generate_random_numbers(number_count)
            
            # Обновляем розыгрыш
            draws[draw_index]['completed'] = True
            draws[draw_index]['numbers'] = winning_numbers
            draws[draw_index]['completed_at'] = datetime.now().isoformat()
            
            if not self.data_manager.save_json(JSON_FILES['draws'], draws_data):
                return None
            
            # Обрабатываем билеты
            winners = self.update_tickets_after_draw(draw_id, winning_numbers)
            total_prize = sum(w['prize'] for w in winners)
            
            logger.info(f"Розыгрыш {draw_id} проведен. Выигрышные числа: {winning_numbers}. Победителей: {len(winners)}")
            
            return {
                "winning_numbers": winning_numbers,
                "draw_id": draw_id,
                "winners": winners,
                "total_prize": total_prize
            }
        except Exception as e:
            logger.error(f"Ошибка проведения розыгрыша: {e}")
            return None
    
    # ========= РАБОТА С БИЛЕТАМИ =========
    
    def get_user_tickets(self, draw_id: Optional[int] = None) -> List[Dict]:
        """Получить билеты пользователя (все или по конкретному розыгрышу)"""
        try:
            tickets_data = self.data_manager.load_json(JSON_FILES['tickets'])
            tickets = tickets_data.get('tickets', [])
            
            if draw_id is not None:
                tickets = [t for t in tickets if t['draw_id'] == draw_id]
                logger.info(f"Найдено {len(tickets)} билетов для розыгрыша {draw_id}")
            else:
                logger.info(f"Загружено {len(tickets)} билетов пользователя")
            
            return tickets
        except Exception as e:
            logger.error(f"Ошибка получения билетов: {e}")
            return []
    
    def add_ticket(self, draw_id: int, numbers: List[int]) -> Optional[Dict]:
        """Добавить новый билет"""
        try:
            tickets_data = self.data_manager.load_json(JSON_FILES['tickets'])
            if 'tickets' not in tickets_data:
                tickets_data['tickets'] = []
            
            ticket = {
                'id': self.get_next_ticket_id(),
                'draw_id': draw_id,
                'numbers': numbers,
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                'matches': 0,
                'prize': 0
            }
            
            tickets_data['tickets'].append(ticket)
            
            if self.data_manager.save_json(JSON_FILES['tickets'], tickets_data):
                logger.info(f"Билет {ticket['id']} успешно добавлен")
                return ticket
            else:
                logger.error("Ошибка сохранения билета")
                return None
        except Exception as e:
            logger.error(f"Ошибка добавления билета: {e}")
            return None
    
    def get_next_ticket_id(self) -> int:
        """Получить следующий ID для билета"""
        try:
            tickets_data = self.data_manager.load_json(JSON_FILES['tickets'])
            tickets = tickets_data.get('tickets', [])
            
            if not tickets:
                return 1
            
            max_id = max(ticket['id'] for ticket in tickets)
            return max_id + 1
        except Exception as e:
            logger.error(f"Ошибка получения следующего ID: {e}")
            return 1
    
    def update_ticket(self, ticket_id: int, new_numbers: List[int]) -> Optional[Dict]:
        """Обновить числа билета"""
        try:
            tickets_data = self.data_manager.load_json(JSON_FILES['tickets'])
            tickets = tickets_data.get('tickets', [])
            
            ticket_index = -1
            target_ticket = None
            
            for i, ticket in enumerate(tickets):
                if ticket['id'] == ticket_id:
                    ticket_index = i
                    target_ticket = ticket
                    break
            
            if not target_ticket:
                return None
            
            # Проверяем, что розыгрыш еще не проведен
            draw = self.get_draw_by_id(target_ticket['draw_id'])
            if not draw or draw.get('completed', False):
                return None
            
            # Валидация новых чисел
            if not Validators.validate_ticket_numbers(new_numbers, draw['type']):
                return None
            
            # Обновляем билет
            tickets[ticket_index]['numbers'] = new_numbers
            tickets[ticket_index]['updated_at'] = datetime.now().isoformat()
            
            if self.data_manager.save_json(JSON_FILES['tickets'], tickets_data):
                logger.info(f"Билет {ticket_id} обновлен")
                return tickets[ticket_index]
            
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления билета {ticket_id}: {e}")
            return None
    
    def update_tickets_after_draw(self, draw_id: int, winning_numbers: List[int]) -> List[Dict]:
        """Обновление статусов билетов после розыгрыша"""
        try:
            tickets_data = self.data_manager.load_json(JSON_FILES['tickets'])
            tickets = tickets_data.get('tickets', [])
            
            draw = self.get_draw_by_id(draw_id)
            if not draw:
                return []
            
            winners = []
            
            for ticket in tickets:
                if ticket.get('draw_id') == draw_id and ticket.get('status') == 'pending':
                    matches = LotteryHelpers.check_winning_ticket(ticket.get('numbers', []), winning_numbers)
                    prize = LotteryHelpers.calculate_prize(matches, draw['type'])
                    
                    ticket['status'] = 'completed'
                    ticket['matches'] = matches
                    ticket['prize'] = prize
                    ticket['draw_completed'] = True
                    ticket['draw_date'] = datetime.now().isoformat()
                    
                    if prize > 0:
                        winners.append({
                            'ticket_id': ticket['id'],
                            'matches': matches,
                            'prize': prize
                        })
            
            self.data_manager.save_json(JSON_FILES['tickets'], tickets_data)
            logger.info(f"Обновлено {len([t for t in tickets if t.get('draw_id') == draw_id])} билетов для розыгрыша {draw_id}")
            
            return winners
        except Exception as e:
            logger.error(f"Ошибка обновления билетов после розыгрыша: {e}")
            return []
    
    # ========= РАБОТА С БАЛАНСОМ =========
    
    def get_balance(self) -> float:
        """Получить баланс пользователя"""
        try:
            balance_data = self.data_manager.load_json(JSON_FILES['balance'])
            balance = balance_data.get('balance', 1500.0)  # Начальный баланс 1500
            logger.info(f"Текущий баланс: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Ошибка получения баланса: {e}")
            return 0.0
    
    def update_balance(self, new_balance: float) -> bool:
        """Обновить баланс пользователя"""
        try:
            if not Validators.validate_balance(new_balance):
                return False
            
            balance_data = {'balance': new_balance}
            if self.data_manager.save_json(JSON_FILES['balance'], balance_data):
                logger.info(f"Баланс обновлен до {new_balance}")
                return True
            else:
                logger.error("Ошибка сохранения баланса")
                return False
        except Exception as e:
            logger.error(f"Ошибка обновления баланса: {e}")
            return False
    
    # ========= РАБОТА С ПАКЕТАМИ =========
    
    def get_packages(self) -> List[Dict]:
        """Получить все пакеты"""
        try:
            packages_data = self.data_manager.load_json(JSON_FILES['packages'])
            packages = packages_data.get('packages', [])
            logger.info(f"Загружено {len(packages)} пакетов")
            return packages
        except Exception as e:
            logger.error(f"Ошибка получения пакетов: {e}")
            return []
    
    def add_package(self, package_data: Dict) -> Optional[Dict]:
        """Добавить новый пакет"""
        try:
            if not Validators.validate_package_data(package_data):
                return None
            
            packages_data = self.data_manager.load_json(JSON_FILES['packages'])
            if 'packages' not in packages_data:
                packages_data['packages'] = []
            
            package = {
                'id': self.data_manager.get_next_id(packages_data['packages']),
                'name': package_data.get('name'),
                'category': package_data.get('category'),
                'price': int(package_data.get('price')),
                'currency': 'COINS',
                'created_date': datetime.now().isoformat()
            }
            
            packages_data['packages'].append(package)
            
            if self.data_manager.save_json(JSON_FILES['packages'], packages_data):
                logger.info(f"Пакет {package['id']} успешно добавлен")
                return package
            else:
                logger.error("Ошибка сохранения пакета")
                return None
        except Exception as e:
            logger.error(f"Ошибка добавления пакета: {e}")
            return None
    
    def update_package(self, package_id: int, package_data: Dict) -> Optional[Dict]:
        """Обновить пакет"""
        try:
            packages_data = self.data_manager.load_json(JSON_FILES['packages'])
            packages = packages_data.get('packages', [])
            
            for i, package in enumerate(packages):
                if package['id'] == package_id:
                    packages[i].update({
                        'name': package_data.get('name', package['name']),
                        'category': package_data.get('category', package['category']),
                        'price': int(package_data.get('price', package['price'])),
                        'updated_date': datetime.now().isoformat()
                    })
                    
                    if self.data_manager.save_json(JSON_FILES['packages'], packages_data):
                        logger.info(f"Пакет {package_id} обновлен")
                        return packages[i]
                    else:
                        logger.error("Ошибка сохранения пакета")
                        return None
            
            logger.warning(f"Пакет с ID {package_id} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка обновления пакета: {e}")
            return None
    
    def delete_package(self, package_id: int) -> bool:
        """Удалить пакет"""
        try:
            packages_data = self.data_manager.load_json(JSON_FILES['packages'])
            packages = packages_data.get('packages', [])
            
            packages_data['packages'] = [p for p in packages if p['id'] != package_id]
            
            if self.data_manager.save_json(JSON_FILES['packages'], packages_data):
                logger.info(f"Пакет {package_id} удален")
                return True
            else:
                logger.error("Ошибка сохранения данных пакетов")
                return False
        except Exception as e:
            logger.error(f"Ошибка удаления пакета: {e}")
            return False
    
    # ========= ПОКУПКА БИЛЕТОВ И ПАКЕТОВ =========
    
    def buy_ticket(self, draw_id: int, numbers: List[int]) -> Dict:
        """Покупка билета"""
        try:
            # Получаем розыгрыш для определения типа
            draw = self.get_draw_by_id(draw_id)
            if not draw:
                return {"success": False, "error": "Розыгрыш не найден", "code": "DRAW_NOT_FOUND"}
            
            # Валидация чисел
            if not Validators.validate_ticket_numbers(numbers, draw['type']):
                return {"success": False, "error": "Неверные числа билета", "code": "INVALID_NUMBERS"}
            
            # Проверка баланса
            current_balance = self.get_balance()
            ticket_price = TICKET_PRICES.get(draw['type'], 10)
            
            if current_balance < ticket_price:
                return {"success": False, "error": "Недостаточно средств", "code": "INSUFFICIENT_FUNDS"}
            
            # Списание средств
            new_balance = current_balance - ticket_price
            if not self.update_balance(new_balance):
                return {"success": False, "error": "Ошибка списания средств", "code": "BALANCE_UPDATE_ERROR"}
            
            # Создание билета
            ticket = self.add_ticket(draw_id, numbers)
            if not ticket:
                # Возвращаем средства в случае ошибки
                self.update_balance(current_balance)
                return {"success": False, "error": "Ошибка создания билета", "code": "TICKET_CREATE_ERROR"}
            
            logger.info(f"Билет {ticket['id']} успешно куплен за {ticket_price}")
            
            return {
                "success": True,
                "data": {
                    "ticket": ticket,
                    "new_balance": new_balance
                },
                "message": "Билет успешно приобретен"
            }
            
        except Exception as e:
            logger.error(f"Ошибка покупки билета: {e}")
            return {"success": False, "error": "Внутренняя ошибка сервера", "code": "INTERNAL_ERROR"}
    
    def buy_package(self, package_type: str) -> Dict:
        """Покупка пакета"""
        try:
            if not Validators.validate_package_type(package_type):
                return {"success": False, "error": "Неверный тип пакета", "code": "INVALID_PACKAGE"}
            
            # Проверка баланса
            current_balance = self.get_balance()
            package_price = PACKAGE_PRICES[package_type]
            
            if current_balance < package_price:
                return {"success": False, "error": "Недостаточно средств", "code": "INSUFFICIENT_FUNDS"}
            
            # Определение розыгрышей по категории пакета
            draws = self.get_all_draws()
            
            if package_type == 'all':
                target_draws = [d for d in draws if not d.get('completed', False)]
            elif package_type == 'big_only':
                target_draws = [d for d in draws if d['type'] == 'big' and not d.get('completed', False)]
            elif package_type == 'express_only':
                target_draws = [d for d in draws if d['type'] == 'express' and not d.get('completed', False)]
            
            if not target_draws:
                return {"success": False, "error": "Нет доступных розыгрышей для пакета", "code": "NO_DRAWS_AVAILABLE"}
            
            # Списание средств
            new_balance = current_balance - package_price
            if not self.update_balance(new_balance):
                return {"success": False, "error": "Ошибка списания средств", "code": "BALANCE_UPDATE_ERROR"}
            
            # Создание билетов для всех розыгрышей
            created_tickets = []
            for draw in target_draws:
                # Генерируем случайные числа для каждого билета
                number_count = 8 if draw['type'] == 'big' else 6
                random_numbers = LotteryHelpers.generate_random_numbers(number_count)
                
                ticket = self.add_ticket(draw['id'], random_numbers)
                if ticket:
                    created_tickets.append(ticket)
            
            if not created_tickets:
                # Возвращаем средства в случае ошибки
                self.update_balance(current_balance)
                return {"success": False, "error": "Ошибка создания билетов", "code": "TICKETS_CREATE_ERROR"}
            
            logger.info(f"Пакет {package_type} успешно куплен, создано билетов: {len(created_tickets)}")
            
            return {
                "success": True,
                "data": {
                    "tickets": created_tickets,
                    "new_balance": new_balance,
                    "package_type": package_type
                },
                "message": f"Пакет успешно приобретен, создано билетов: {len(created_tickets)}"
            }
            
        except Exception as e:
            logger.error(f"Ошибка покупки пакета: {e}")
            return {"success": False, "error": "Внутренняя ошибка сервера", "code": "INTERNAL_ERROR"}
    
    # ========= СТАТИСТИКА =========
    
    def calculate_tickets_stats(self) -> Dict:
        """Расчет статистики по билетам для админки"""
        try:
            tickets = self.get_user_tickets()
            
            total_tickets = len(tickets)
            winning_tickets = sum(1 for ticket in tickets if ticket.get('prize', 0) > 0)
            pending_tickets = sum(1 for ticket in tickets if ticket.get('status') == 'pending')
            
            return {
                'total_tickets': total_tickets,
                'winning_tickets': winning_tickets,
                'pending_tickets': pending_tickets
            }
        except Exception as e:
            logger.error(f"Ошибка расчета статистики билетов: {e}")
            return {'total_tickets': 0, 'winning_tickets': 0, 'pending_tickets': 0}
    
    def get_stats(self) -> Dict:
        """Получить общую статистику"""
        try:
            draws = self.get_all_draws()
            packages = self.get_packages()
            
            stats = {
                'total_draws': len(draws),
                'active_draws': len([d for d in draws if not d.get('completed')]),
                'completed_draws': len([d for d in draws if d.get('completed')]),
                'total_packages': len(packages),
                'current_balance': self.get_balance(),
                **self.calculate_tickets_stats()
            }
            
            return stats
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {
                'total_draws': 0,
                'active_draws': 0,
                'completed_draws': 0,
                'total_packages': 0,
                'current_balance': 0,
                'total_tickets': 0,
                'winning_tickets': 0,
                'pending_tickets': 0
            }   
        
# В models/lottery.py
def is_draw_active(self, draw_id):
    """Проверка активности розыгрыша"""
    draw = self.get_draw_by_id(draw_id)
    return draw and not draw.get('completed', False)

def get_user_tickets_count(self, draw_id=None):
    """Получить количество билетов пользователя"""
    tickets = self.get_user_tickets(draw_id)
    return len(tickets)

def can_buy_ticket(self, draw_id, user_balance=None):
    """Проверка возможности покупки билета"""
    draw = self.get_draw_by_id(draw_id)
    if not draw or draw.get('completed', False):
        return False, "Розыгрыш недоступен"
    
    if user_balance is None:
        user_balance = self.get_balance()
    
    ticket_price = draw.get('cost', 100)
    if user_balance < ticket_price:
        return False, "Недостаточно средств"
    
    return True, "OK"