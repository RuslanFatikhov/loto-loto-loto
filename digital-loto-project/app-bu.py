from flask import Flask, render_template, request, jsonify, abort
import json
import os
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional, Union

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Константы
JSON_FILES = {
    'draws': 'data/draws.json',
    'tickets': 'data/tickets.json',
    'balance': 'data/balance.json',
    'banners': 'data/banners.json'
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

# =============================================================================
# ФУНКЦИИ РАБОТЫ С JSON
# =============================================================================

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

def get_draw_by_id(draw_id: int) -> Optional[Dict]:
    """Получить розыгрыш по ID"""
    try:
        draws = load_json(JSON_FILES['draws'])
        for draw in draws.get('draws', []):
            if draw['id'] == draw_id:
                logger.info(f"Найден розыгрыш с ID {draw_id}")
                return draw
        
        logger.warning(f"Розыгрыш с ID {draw_id} не найден")
        return None
    except Exception as e:
        logger.error(f"Ошибка получения розыгрыша {draw_id}: {e}")
        return None

def get_user_tickets(draw_id: Optional[int] = None) -> List[Dict]:
    """Получить билеты пользователя (все или по конкретному розыгрышу)"""
    try:
        tickets_data = load_json(JSON_FILES['tickets'])
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

def add_ticket(draw_id: int, numbers: List[int]) -> Optional[Dict]:
    """Добавить новый билет"""
    try:
        tickets_data = load_json(JSON_FILES['tickets'])
        if 'tickets' not in tickets_data:
            tickets_data['tickets'] = []
        
        ticket = {
            'id': get_next_ticket_id(),
            'draw_id': draw_id,
            'numbers': numbers,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'matches': 0,
            'prize': 0
        }
        
        tickets_data['tickets'].append(ticket)
        
        if save_json(JSON_FILES['tickets'], tickets_data):
            logger.info(f"Билет {ticket['id']} успешно добавлен")
            return ticket
        else:
            logger.error("Ошибка сохранения билета")
            return None
    except Exception as e:
        logger.error(f"Ошибка добавления билета: {e}")
        return None

def get_balance() -> float:
    """Получить баланс пользователя"""
    try:
        balance_data = load_json(JSON_FILES['balance'])
        balance = balance_data.get('balance', 100.0)  # Начальный баланс 100
        logger.info(f"Текущий баланс: {balance}")
        return balance
    except Exception as e:
        logger.error(f"Ошибка получения баланса: {e}")
        return 0.0

def update_balance(new_balance: float) -> bool:
    """Обновить баланс пользователя"""
    try:
        balance_data = {'balance': new_balance}
        if save_json(JSON_FILES['balance'], balance_data):
            logger.info(f"Баланс обновлен до {new_balance}")
            return True
        else:
            logger.error("Ошибка сохранения баланса")
            return False
    except Exception as e:
        logger.error(f"Ошибка обновления баланса: {e}")
        return False

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def generate_random_numbers(count: int, max_number: int = 36) -> List[int]:
    """Генерация случайных чисел для розыгрыша"""
    try:
        numbers = random.sample(range(1, max_number + 1), count)
        numbers.sort()
        logger.info(f"Сгенерированы числа: {numbers}")
        return numbers
    except Exception as e:
        logger.error(f"Ошибка генерации случайных чисел: {e}")
        return []

def check_winning_ticket(ticket_numbers: List[int], draw_numbers: List[int]) -> int:
    """Проверка выигрышного билета - возвращает количество совпадений"""
    try:
        matches = len(set(ticket_numbers) & set(draw_numbers))
        logger.info(f"Найдено {matches} совпадений")
        return matches
    except Exception as e:
        logger.error(f"Ошибка проверки билета: {e}")
        return 0

def get_next_ticket_id() -> int:
    """Получить следующий ID для билета"""
    try:
        tickets_data = load_json(JSON_FILES['tickets'])
        tickets = tickets_data.get('tickets', [])
        
        if not tickets:
            return 1
        
        max_id = max(ticket['id'] for ticket in tickets)
        return max_id + 1
    except Exception as e:
        logger.error(f"Ошибка получения следующего ID: {e}")
        return 1

def filter_tickets(tickets: List[Dict], status: Optional[str] = None, draw_id: Optional[int] = None) -> List[Dict]:
    """Фильтрация билетов по статусу и розыгрышу"""
    try:
        filtered = tickets
        
        if status:
            filtered = [t for t in filtered if t['status'] == status]
        
        if draw_id:
            filtered = [t for t in filtered if t['draw_id'] == draw_id]
        
        logger.info(f"Отфильтровано {len(filtered)} билетов")
        return filtered
    except Exception as e:
        logger.error(f"Ошибка фильтрации билетов: {e}")
        return []

def calculate_prize(matches: int, draw_type: str) -> float:
    """Вычисление размера приза на основе количества совпадений"""
    prize_table = {
        'big': {8: 1000000, 7: 50000, 6: 5000, 5: 500, 4: 50},
        'express': {6: 500000, 5: 25000, 4: 2500, 3: 250}
    }
    
    return prize_table.get(draw_type, {}).get(matches, 0)

def validate_ticket_numbers(numbers: List[int], draw_type: str) -> bool:
    """Валидация чисел билета"""
    required_count = 8 if draw_type == 'big' else 6
    
    if len(numbers) != required_count:
        return False
    
    if not all(1 <= num <= 36 for num in numbers):
        return False
    
    if len(set(numbers)) != len(numbers):  # Проверка на дубликаты
        return False
    
    return True

# =============================================================================
# ОСНОВНЫЕ МАРШРУТЫ
# =============================================================================

@app.route('/')
def index():
    """Главная страница"""
    try:
        draws_data = load_json(JSON_FILES['draws'])
        banners_data = load_json(JSON_FILES['banners'])
        balance = get_balance()
        
        # Безопасное извлечение данных
        draws = draws_data.get('draws', []) if isinstance(draws_data, dict) else draws_data if isinstance(draws_data, list) else []
        banners = banners_data.get('banners', []) if isinstance(banners_data, dict) else banners_data if isinstance(banners_data, list) else []
        
        return render_template('index.html', 
                             draws=draws, 
                             banners=banners,
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки главной страницы: {e}")
        abort(500)

@app.route('/tickets')
def tickets():
    """Страница билетов"""
    try:
        user_tickets = get_user_tickets()
        draws_data = load_json(JSON_FILES['draws'])
        balance = get_balance()
        
        # Безопасное извлечение данных
        draws = draws_data.get('draws', []) if isinstance(draws_data, dict) else draws_data if isinstance(draws_data, list) else []
        
        return render_template('tickets.html', 
                             tickets=user_tickets, 
                             draws=draws,
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки страницы билетов: {e}")
        abort(500)


@app.route('/draw/<int:draw_id>')
def draw_detail(draw_id):
    """Страница конкретного розыгрыша"""
    try:
        draw = get_draw_by_id(draw_id)
        if not draw:
            abort(404)
        
        user_tickets = get_user_tickets(draw_id)
        balance = get_balance()
        
        return render_template('draw.html', 
                             draw=draw, 
                             tickets=user_tickets,
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки страницы розыгрыша {draw_id}: {e}")
        abort(500)

@app.route('/admin')
def admin():
    """Админка"""
    try:
        draws_data = load_json(JSON_FILES['draws'])
        tickets_data = load_json(JSON_FILES['tickets'])
        balance = get_balance()
        
        # Безопасное извлечение данных
        draws = draws_data.get('draws', []) if isinstance(draws_data, dict) else draws_data if isinstance(draws_data, list) else []
        tickets = tickets_data.get('tickets', []) if isinstance(tickets_data, dict) else tickets_data if isinstance(tickets_data, list) else []
        
        return render_template('admin.html', 
                             draws=draws, 
                             tickets=tickets,
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки админки: {e}")
        abort(500)

# =============================================================================
# API МАРШРУТЫ ДЛЯ AJAX
# =============================================================================

@app.route('/api/buy_ticket', methods=['POST'])
def buy_ticket():
    """Покупка билета"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные",
                "code": "NO_DATA"
            }), 400
        
        draw_id = data.get('draw_id')
        numbers = data.get('numbers', [])
        
        # Валидация данных
        if not draw_id or not numbers:
            return jsonify({
                "success": False,
                "error": "Не указаны обязательные поля",
                "code": "MISSING_FIELDS"
            }), 400
        
        # Получаем розыгрыш для определения типа
        draw = get_draw_by_id(draw_id)
        if not draw:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден",
                "code": "DRAW_NOT_FOUND"
            }), 404
        
        # Валидация чисел
        if not validate_ticket_numbers(numbers, draw['type']):
            return jsonify({
                "success": False,
                "error": "Неверные числа билета",
                "code": "INVALID_NUMBERS"
            }), 400
        
        # Проверка баланса
        current_balance = get_balance()
        ticket_price = TICKET_PRICES.get(draw['type'], 10)
        
        if current_balance < ticket_price:
            return jsonify({
                "success": False,
                "error": "Недостаточно средств",
                "code": "INSUFFICIENT_FUNDS"
            }), 400
        
        # Списание средств
        new_balance = current_balance - ticket_price
        if not update_balance(new_balance):
            return jsonify({
                "success": False,
                "error": "Ошибка списания средств",
                "code": "BALANCE_UPDATE_ERROR"
            }), 500
        
        # Создание билета
        ticket = add_ticket(draw_id, numbers)
        if not ticket:
            # Возвращаем средства в случае ошибки
            update_balance(current_balance)
            return jsonify({
                "success": False,
                "error": "Ошибка создания билета",
                "code": "TICKET_CREATE_ERROR"
            }), 500
        
        logger.info(f"Билет {ticket['id']} успешно куплен за {ticket_price}")
        
        return jsonify({
            "success": True,
            "data": {
                "ticket": ticket,
                "new_balance": new_balance
            },
            "message": "Билет успешно приобретен"
        })
        
    except Exception as e:
        logger.error(f"Ошибка покупки билета: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/buy_package', methods=['POST'])
def buy_package():
    """Покупка пакета"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные",
                "code": "NO_DATA"
            }), 400
        
        package_type = data.get('package_type')
        
        if package_type not in PACKAGE_PRICES:
            return jsonify({
                "success": False,
                "error": "Неверный тип пакета",
                "code": "INVALID_PACKAGE"
            }), 400
        
        # Проверка баланса
        current_balance = get_balance()
        package_price = PACKAGE_PRICES[package_type]
        
        if current_balance < package_price:
            return jsonify({
                "success": False,
                "error": "Недостаточно средств",
                "code": "INSUFFICIENT_FUNDS"
            }), 400
        
        # Определение розыгрышей по категории пакета
        draws_data = load_json(JSON_FILES['draws'])
        draws = draws_data.get('draws', [])
        
        if package_type == 'all':
            target_draws = [d for d in draws if not d.get('completed', False)]
        elif package_type == 'big_only':
            target_draws = [d for d in draws if d['type'] == 'big' and not d.get('completed', False)]
        elif package_type == 'express_only':
            target_draws = [d for d in draws if d['type'] == 'express' and not d.get('completed', False)]
        
        if not target_draws:
            return jsonify({
                "success": False,
                "error": "Нет доступных розыгрышей для пакета",
                "code": "NO_DRAWS_AVAILABLE"
            }), 400
        
        # Списание средств
        new_balance = current_balance - package_price
        if not update_balance(new_balance):
            return jsonify({
                "success": False,
                "error": "Ошибка списания средств",
                "code": "BALANCE_UPDATE_ERROR"
            }), 500
        
        # Создание билетов для всех розыгрышей (пока без чисел)
        created_tickets = []
        for draw in target_draws:
            # Генерируем случайные числа для каждого билета
            number_count = 8 if draw['type'] == 'big' else 6
            random_numbers = generate_random_numbers(number_count)
            
            ticket = add_ticket(draw['id'], random_numbers)
            if ticket:
                created_tickets.append(ticket)
        
        if not created_tickets:
            # Возвращаем средства в случае ошибки
            update_balance(current_balance)
            return jsonify({
                "success": False,
                "error": "Ошибка создания билетов",
                "code": "TICKETS_CREATE_ERROR"
            }), 500
        
        logger.info(f"Пакет {package_type} успешно куплен, создано билетов: {len(created_tickets)}")
        
        return jsonify({
            "success": True,
            "data": {
                "tickets": created_tickets,
                "new_balance": new_balance,
                "package_type": package_type
            },
            "message": f"Пакет успешно приобретен, создано билетов: {len(created_tickets)}"
        })
        
    except Exception as e:
        logger.error(f"Ошибка покупки пакета: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/balance', methods=['GET'])
def get_balance_api():
    """Получить текущий баланс"""
    try:
        balance = get_balance()
        return jsonify({
            "success": True,
            "data": {"balance": balance},
            "message": "Баланс получен"
        })
    except Exception as e:
        logger.error(f"Ошибка получения баланса: {e}")
        return jsonify({
            "success": False,
            "error": "Ошибка получения баланса",
            "code": "BALANCE_ERROR"
        }), 500

@app.route('/api/update_balance', methods=['POST'])
def update_balance_api():
    """Обновить баланс (для админки)"""
    try:
        data = request.get_json()
        
        if not data or 'balance' not in data:
            return jsonify({
                "success": False,
                "error": "Не указан баланс",
                "code": "MISSING_BALANCE"
            }), 400
        
        new_balance = float(data['balance'])
        
        if new_balance < 0:
            return jsonify({
                "success": False,
                "error": "Баланс не может быть отрицательным",
                "code": "NEGATIVE_BALANCE"
            }), 400
        
        if update_balance(new_balance):
            return jsonify({
                "success": True,
                "data": {"balance": new_balance},
                "message": "Баланс обновлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка обновления баланса",
                "code": "UPDATE_ERROR"
            }), 500
        
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Неверный формат баланса",
            "code": "INVALID_BALANCE_FORMAT"
        }), 400
    except Exception as e:
        logger.error(f"Ошибка обновления баланса: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/conduct_draw', methods=['POST'])
def conduct_draw():
    """Провести розыгрыш (для админки)"""
    try:
        data = request.get_json()
        
        if not data or 'draw_id' not in data:
            return jsonify({
                "success": False,
                "error": "Не указан ID розыгрыша",
                "code": "MISSING_DRAW_ID"
            }), 400
        
        draw_id = int(data['draw_id'])
        
        # Получаем розыгрыш
        draws_data = load_json(JSON_FILES['draws'])
        draws = draws_data.get('draws', [])
        
        draw_index = -1
        target_draw = None
        
        for i, draw in enumerate(draws):
            if draw['id'] == draw_id:
                draw_index = i
                target_draw = draw
                break
        
        if not target_draw:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден",
                "code": "DRAW_NOT_FOUND"
            }), 404
        
        if target_draw.get('completed', False):
            return jsonify({
                "success": False,
                "error": "Розыгрыш уже проведен",
                "code": "DRAW_COMPLETED"
            }), 400
        
        # Генерируем выигрышные числа
        number_count = 8 if target_draw['type'] == 'big' else 6
        winning_numbers = generate_random_numbers(number_count)
        
        # Обновляем розыгрыш
        draws[draw_index]['completed'] = True
        draws[draw_index]['numbers'] = winning_numbers
        draws[draw_index]['completed_at'] = datetime.now().isoformat()
        
        if not save_json(JSON_FILES['draws'], draws_data):
            return jsonify({
                "success": False,
                "error": "Ошибка сохранения розыгрыша",
                "code": "SAVE_ERROR"
            }), 500
        
        # Обрабатываем билеты
        tickets_data = load_json(JSON_FILES['tickets'])
        tickets = tickets_data.get('tickets', [])
        
        winners = []
        total_prize = 0
        
        for i, ticket in enumerate(tickets):
            if ticket['draw_id'] == draw_id and ticket['status'] == 'pending':
                matches = check_winning_ticket(ticket['numbers'], winning_numbers)
                prize = calculate_prize(matches, target_draw['type'])
                
                tickets[i]['matches'] = matches
                tickets[i]['prize'] = prize
                tickets[i]['status'] = 'completed'
                
                if prize > 0:
                    winners.append({
                        'ticket_id': ticket['id'],
                        'matches': matches,
                        'prize': prize
                    })
                    total_prize += prize
        
        # Сохраняем обновленные билеты
        if not save_json(JSON_FILES['tickets'], tickets_data):
            logger.error("Ошибка сохранения билетов после розыгрыша")
        
        logger.info(f"Розыгрыш {draw_id} проведен. Выигрышные числа: {winning_numbers}. Победителей: {len(winners)}")
        
        return jsonify({
            "success": True,
            "data": {
                "draw_id": draw_id,
                "winning_numbers": winning_numbers,
                "winners": winners,
                "total_prize": total_prize
            },
            "message": f"Розыгрыш проведен. Победителей: {len(winners)}"
        })
        
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "error": "Неверный формат ID розыгрыша",
            "code": "INVALID_DRAW_ID"
        }), 400
    except Exception as e:
        logger.error(f"Ошибка проведения розыгрыша: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/draws', methods=['GET'])
def get_draws_api():
    """Получить все розыгрыши"""
    try:
        draws = load_json(JSON_FILES['draws'])
        return jsonify({
            "success": True,
            "data": draws,
            "message": "Розыгрыши получены"
        })
    except Exception as e:
        logger.error(f"Ошибка получения розыгрышей: {e}")
        return jsonify({
            "success": False,
            "error": "Ошибка получения розыгрышей",
            "code": "DRAWS_ERROR"
        }), 500

@app.route('/api/draws', methods=['POST'])
def add_draw_api():
    """Добавить новый розыгрыш"""
    try:
        data = request.get_json()
        
        required_fields = ['title', 'type', 'date', 'time']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "error": "Не все обязательные поля заполнены",
                "code": "MISSING_FIELDS"
            }), 400
        
        draws_data = load_json(JSON_FILES['draws'])
        if 'draws' not in draws_data:
            draws_data['draws'] = []
        
        # Получаем следующий ID
        next_id = 1
        if draws_data['draws']:
            next_id = max(draw['id'] for draw in draws_data['draws']) + 1
        
        new_draw = {
            'id': next_id,
            'title': data['title'],
            'type': data['type'],
            'date': data['date'],
            'time': data['time'],
            'prize': data.get('prize', 0),
            'completed': False,
            'numbers': [],
            'created_at': datetime.now().isoformat()
        }
        
        draws_data['draws'].append(new_draw)
        
        if save_json(JSON_FILES['draws'], draws_data):
            logger.info(f"Новый розыгрыш {next_id} добавлен")
            return jsonify({
                "success": True,
                "data": new_draw,
                "message": "Розыгрыш добавлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка сохранения розыгрыша",
                "code": "SAVE_ERROR"
            }), 500
        
    except Exception as e:
        logger.error(f"Ошибка добавления розыгрыша: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/draws/<int:draw_id>', methods=['PUT'])
def update_draw_api(draw_id):
    """Обновить розыгрыш"""
    try:
        data = request.get_json()
        
        draws_data = load_json(JSON_FILES['draws'])
        draws = draws_data.get('draws', [])
        
        draw_index = -1
        for i, draw in enumerate(draws):
            if draw['id'] == draw_id:
                draw_index = i
                break
        
        if draw_index == -1:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден",
                "code": "DRAW_NOT_FOUND"
            }), 404
        
        # Обновляем поля
        updatable_fields = ['title', 'type', 'date', 'time', 'prize']
        for field in updatable_fields:
            if field in data:
                draws[draw_index][field] = data[field]
        
        draws[draw_index]['updated_at'] = datetime.now().isoformat()
        
        if save_json(JSON_FILES['draws'], draws_data):
            logger.info(f"Розыгрыш {draw_id} обновлен")
            return jsonify({
                "success": True,
                "data": draws[draw_index],
                "message": "Розыгрыш обновлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка сохранения розыгрыша",
                "code": "SAVE_ERROR"
            }), 500
        
    except Exception as e:
        logger.error(f"Ошибка обновления розыгрыша {draw_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/draws/<int:draw_id>', methods=['DELETE'])
def delete_draw_api(draw_id):
    """Удалить розыгрыш"""
    try:
        draws_data = load_json(JSON_FILES['draws'])
        draws = draws_data.get('draws', [])
        
        # Находим розыгрыш для удаления
        draw_to_delete = None
        new_draws = []
        
        for draw in draws:
            if draw['id'] == draw_id:
                draw_to_delete = draw
            else:
                new_draws.append(draw)
        
        if not draw_to_delete:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден",
                "code": "DRAW_NOT_FOUND"
            }), 404
        
        # Проверяем, есть ли билеты на этот розыгрыш
        user_tickets = get_user_tickets(draw_id)
        if user_tickets:
            return jsonify({
                "success": False,
                "error": "Нельзя удалить розыгрыш с купленными билетами",
                "code": "DRAW_HAS_TICKETS"
            }), 400
        
        draws_data['draws'] = new_draws
        
        if save_json(JSON_FILES['draws'], draws_data):
            logger.info(f"Розыгрыш {draw_id} удален")
            return jsonify({
                "success": True,
                "data": {"deleted_draw_id": draw_id},
                "message": "Розыгрыш удален"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка сохранения данных",
                "code": "SAVE_ERROR"
            }), 500
        
    except Exception as e:
        logger.error(f"Ошибка удаления розыгрыша {draw_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ API МАРШРУТЫ
# =============================================================================

@app.route('/api/tickets', methods=['GET'])
def get_tickets_api():
    """Получить билеты пользователя с фильтрацией"""
    try:
        draw_id = request.args.get('draw_id', type=int)
        status = request.args.get('status')
        
        all_tickets = get_user_tickets()
        filtered_tickets = filter_tickets(all_tickets, status=status, draw_id=draw_id)
        
        return jsonify({
            "success": True,
            "data": {"tickets": filtered_tickets},
            "message": f"Найдено {len(filtered_tickets)} билетов"
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения билетов: {e}")
        return jsonify({
            "success": False,
            "error": "Ошибка получения билетов",
            "code": "TICKETS_ERROR"
        }), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket_api(ticket_id):
    """Обновить числа билета (до проведения розыгрыша)"""
    try:
        data = request.get_json()
        
        if not data or 'numbers' not in data:
            return jsonify({
                "success": False,
                "error": "Не указаны числа билета",
                "code": "MISSING_NUMBERS"
            }), 400
        
        new_numbers = data['numbers']
        
        tickets_data = load_json(JSON_FILES['tickets'])
        tickets = tickets_data.get('tickets', [])
        
        ticket_index = -1
        target_ticket = None
        
        for i, ticket in enumerate(tickets):
            if ticket['id'] == ticket_id:
                ticket_index = i
                target_ticket = ticket
                break
        
        if not target_ticket:
            return jsonify({
                "success": False,
                "error": "Билет не найден",
                "code": "TICKET_NOT_FOUND"
            }), 404
        
        # Проверяем, что розыгрыш еще не проведен
        draw = get_draw_by_id(target_ticket['draw_id'])
        if not draw:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден",
                "code": "DRAW_NOT_FOUND"
            }), 404
        
        if draw.get('completed', False):
            return jsonify({
                "success": False,
                "error": "Нельзя изменить билет после проведения розыгрыша",
                "code": "DRAW_COMPLETED"
            }), 400
        
        # Валидация новых чисел
        if not validate_ticket_numbers(new_numbers, draw['type']):
            return jsonify({
                "success": False,
                "error": "Неверные числа билета",
                "code": "INVALID_NUMBERS"
            }), 400
        
        # Обновляем билет
        tickets[ticket_index]['numbers'] = new_numbers
        tickets[ticket_index]['updated_at'] = datetime.now().isoformat()
        
        if save_json(JSON_FILES['tickets'], tickets_data):
            logger.info(f"Билет {ticket_id} обновлен")
            return jsonify({
                "success": True,
                "data": {"ticket": tickets[ticket_index]},
                "message": "Билет обновлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка сохранения билета",
                "code": "SAVE_ERROR"
            }), 500
        
    except Exception as e:
        logger.error(f"Ошибка обновления билета {ticket_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics_api():
    """Получить статистику для админки"""
    try:
        # Загружаем данные
        draws_data = load_json(JSON_FILES['draws'])
        tickets_data = load_json(JSON_FILES['tickets'])
        
        draws = draws_data.get('draws', [])
        tickets = tickets_data.get('tickets', [])
        
        # Подсчитываем статистику
        total_draws = len(draws)
        completed_draws = len([d for d in draws if d.get('completed', False)])
        pending_draws = total_draws - completed_draws
        
        total_tickets = len(tickets)
        completed_tickets = len([t for t in tickets if t['status'] == 'completed'])
        pending_tickets = len([t for t in tickets if t['status'] == 'pending'])
        
        winning_tickets = len([t for t in tickets if t.get('prize', 0) > 0])
        total_prizes = sum(t.get('prize', 0) for t in tickets)
        
        # Статистика по типам розыгрышей
        big_draws = len([d for d in draws if d['type'] == 'big'])
        express_draws = len([d for d in draws if d['type'] == 'express'])
        
        # Статистика продаж
        big_tickets = len([t for t in tickets if get_draw_by_id(t['draw_id']) and get_draw_by_id(t['draw_id'])['type'] == 'big'])
        express_tickets = len([t for t in tickets if get_draw_by_id(t['draw_id']) and get_draw_by_id(t['draw_id'])['type'] == 'express'])
        
        revenue = big_tickets * TICKET_PRICES['big'] + express_tickets * TICKET_PRICES['express']
        
        statistics = {
            "draws": {
                "total": total_draws,
                "completed": completed_draws,
                "pending": pending_draws,
                "big_draws": big_draws,
                "express_draws": express_draws
            },
            "tickets": {
                "total": total_tickets,
                "completed": completed_tickets,
                "pending": pending_tickets,
                "winning": winning_tickets,
                "big_tickets": big_tickets,
                "express_tickets": express_tickets
            },
            "financial": {
                "revenue": revenue,
                "total_prizes": total_prizes,
                "profit": revenue - total_prizes,
                "current_balance": get_balance()
            }
        }
        
        return jsonify({
            "success": True,
            "data": statistics,
            "message": "Статистика получена"
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({
            "success": False,
            "error": "Ошибка получения статистики",
            "code": "STATISTICS_ERROR"
        }), 500

@app.route('/api/winners/<int:draw_id>', methods=['GET'])
def get_winners_api(draw_id):
    """Получить список победителей конкретного розыгрыша"""
    try:
        draw = get_draw_by_id(draw_id)
        if not draw:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден",
                "code": "DRAW_NOT_FOUND"
            }), 404
        
        if not draw.get('completed', False):
            return jsonify({
                "success": False,
                "error": "Розыгрыш еще не проведен",
                "code": "DRAW_NOT_COMPLETED"
            }), 400
        
        # Получаем все билеты этого розыгрыша с призами
        tickets = get_user_tickets(draw_id)
        winners = [
            {
                "ticket_id": ticket['id'],
                "numbers": ticket['numbers'],
                "matches": ticket.get('matches', 0),
                "prize": ticket.get('prize', 0),
                "created_at": ticket.get('created_at')
            }
            for ticket in tickets
            if ticket.get('prize', 0) > 0
        ]
        
        # Сортируем по размеру приза (по убыванию)
        winners.sort(key=lambda x: x['prize'], reverse=True)
        
        return jsonify({
            "success": True,
            "data": {
                "draw": draw,
                "winners": winners,
                "total_winners": len(winners),
                "total_prize_amount": sum(w['prize'] for w in winners)
            },
            "message": f"Найдено {len(winners)} победителей"
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения победителей розыгрыша {draw_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

# =============================================================================
# ОБРАБОТЧИКИ ОШИБОК
# =============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Обработчик ошибки 404"""
    if request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "error": "Ресурс не найден",
            "code": "NOT_FOUND"
        }), 404
    else:
        return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    logger.error(f"Внутренняя ошибка сервера: {error}")
    
    if request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500
    else:
        return render_template('500.html'), 500

@app.errorhandler(400)
def bad_request_error(error):
    """Обработчик ошибки 400"""
    if request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "error": "Неверный запрос",
            "code": "BAD_REQUEST"
        }), 400
    else:
        return "Неверный запрос", 400

# =============================================================================
# ИНИЦИАЛИЗАЦИЯ ДАННЫХ
# =============================================================================

def init_data_files():
    """Инициализация файлов данных при первом запуске"""
    try:
        # Создаем директорию data если не существует
        os.makedirs('data', exist_ok=True)
        
        # Инициализируем файлы с базовыми данными если они не существуют
        if not os.path.exists(JSON_FILES['draws']):
            initial_draws = {
                "draws": [
                    {
                        "id": 1,
                        "title": "Большое Лото #1",
                        "type": "big",
                        "date": "2025-08-15",
                        "time": "20:00",
                        "prize": 1000000,
                        "completed": False,
                        "numbers": [],
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "title": "Экспресс Лото #1",
                        "type": "express",
                        "date": "2025-08-15",
                        "time": "12:00",
                        "prize": 500000,
                        "completed": False,
                        "numbers": [],
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            save_json(JSON_FILES['draws'], initial_draws)
            logger.info("Инициализированы данные розыгрышей")
        
        if not os.path.exists(JSON_FILES['tickets']):
            initial_tickets = {"tickets": []}
            save_json(JSON_FILES['tickets'], initial_tickets)
            logger.info("Инициализирован файл билетов")
        
        if not os.path.exists(JSON_FILES['balance']):
            initial_balance = {"balance": 100.0}
            save_json(JSON_FILES['balance'], initial_balance)
            logger.info("Инициализирован баланс пользователя: 100.0")
        else:
            # Проверяем текущий баланс и устанавливаем минимальный если он 0
            current_balance_data = load_json(JSON_FILES['balance'])
            current_balance = current_balance_data.get('balance', 0) if isinstance(current_balance_data, dict) else 0
            if current_balance <= 0:
                initial_balance = {"balance": 100.0}
                save_json(JSON_FILES['balance'], initial_balance)
                logger.info("Баланс был 0, установлен начальный баланс: 100.0")
        
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
            save_json(JSON_FILES['banners'], initial_banners)
            logger.info("Инициализированы баннеры")
        
    except Exception as e:
        logger.error(f"Ошибка инициализации данных: {e}")

# =============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# =============================================================================

if __name__ == '__main__':
    # Инициализируем данные при запуске
    init_data_files()
    
    # Запускаем приложение
    logger.info("Запуск приложения Flask для цифрового Лото")
    app.run(debug=True, host='0.0.0.0', port=5700)