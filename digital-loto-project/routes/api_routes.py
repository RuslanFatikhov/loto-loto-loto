"""
API маршруты для AJAX запросов
"""
import logging
from flask import Blueprint, request, jsonify
from models.lottery import LotteryService
from utils.helpers import TicketGrouping

logger = logging.getLogger(__name__)

# Создаем Blueprint для API маршрутов
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Инициализируем сервис
lottery_service = LotteryService()

@api_bp.route('/buy_ticket', methods=['POST'])
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
        
        # Покупаем билет через сервис
        result = lottery_service.buy_ticket(draw_id, numbers)
        
        if result["success"]:
            return jsonify(result)
        else:
            status_code = 404 if result["code"] == "DRAW_NOT_FOUND" else 400
            return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Ошибка покупки билета: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@api_bp.route('/buy_package', methods=['POST'])
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
        
        if not package_type:
            return jsonify({
                "success": False,
                "error": "Не указан тип пакета",
                "code": "MISSING_PACKAGE_TYPE"
            }), 400
        
        # Покупаем пакет через сервис
        result = lottery_service.buy_package(package_type)
        
        if result["success"]:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Ошибка покупки пакета: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@api_bp.route('/balance', methods=['GET'])
def get_balance():
    """Получить текущий баланс"""
    try:
        balance = lottery_service.get_balance()
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

@api_bp.route('/tickets')
def get_filtered_tickets():
    """API для получения отфильтрованных билетов"""
    try:
        status = request.args.get('status', 'all')
        draw_id = request.args.get('draw_id', 'all')
        
        user_tickets = lottery_service.get_user_tickets()
        draws = lottery_service.get_all_draws()
        
        # Применяем фильтры
        filtered_tickets = TicketGrouping.apply_ticket_filters(user_tickets, draws, status, draw_id)
        
        return jsonify({
            'success': True,
            'tickets': filtered_tickets,
            'count': len(filtered_tickets)
        })
    except Exception as e:
        logger.error(f"Ошибка получения билетов: {e}")
        return jsonify({
            'success': False,
            'tickets': [],
            'count': 0
        }), 500

@api_bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
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
        
        # Обновляем билет через сервис
        updated_ticket = lottery_service.update_ticket(ticket_id, new_numbers)
        
        if updated_ticket:
            return jsonify({
                "success": True,
                "data": {"ticket": updated_ticket},
                "message": "Билет обновлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Билет не найден или нельзя изменить",
                "code": "TICKET_UPDATE_ERROR"
            }), 404
        
    except Exception as e:
        logger.error(f"Ошибка обновления билета {ticket_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500