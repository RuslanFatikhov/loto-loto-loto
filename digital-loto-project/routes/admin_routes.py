"""
Админские API маршруты
"""
import logging
from flask import Blueprint, request, jsonify
from models.lottery import LotteryService

logger = logging.getLogger(__name__)

# Создаем Blueprint для админских API маршрутов
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Инициализируем сервис
lottery_service = LotteryService()

# ========= УПРАВЛЕНИЕ БАЛАНСОМ =========

@admin_bp.route('/update_balance', methods=['POST'])
def update_balance():
    """Обновить баланс (для админки)"""
    try:
        data = request.get_json()
        
        if not data or 'balance' not in data:
            return jsonify({
                "success": False,
                "error": "Не указан баланс",
                "code": "MISSING_BALANCE"
            }), 400
        
        try:
            new_balance = float(data['balance'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Неверный формат баланса",
                "code": "INVALID_BALANCE_FORMAT"
            }), 400
        
        if new_balance < 0:
            return jsonify({
                "success": False,
                "error": "Баланс не может быть отрицательным",
                "code": "NEGATIVE_BALANCE"
            }), 400
        
        if lottery_service.update_balance(new_balance):
            return jsonify({
                "success": True,
                "new_balance": new_balance,
                "message": "Баланс обновлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Ошибка обновления баланса",
                "code": "UPDATE_ERROR"
            }), 500
        
    except Exception as e:
        logger.error(f"Ошибка обновления баланса: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

# ========= УПРАВЛЕНИЕ РОЗЫГРЫШАМИ =========

@admin_bp.route('/conduct_draw', methods=['POST'])
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
        
        try:
            draw_id = int(data['draw_id'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error": "Неверный формат ID розыгрыша",
                "code": "INVALID_DRAW_ID"
            }), 400
        
        # Проводим розыгрыш через сервис
        result = lottery_service.conduct_draw(draw_id)
        
        if result:
            return jsonify({
                "success": True,
                **result,
                "message": f"Розыгрыш проведен. Победителей: {len(result['winners'])}"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден или уже проведен",
                "code": "DRAW_ERROR"
            }), 400
        
    except Exception as e:
        logger.error(f"Ошибка проведения розыгрыша: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@admin_bp.route('/draws', methods=['GET'])
def get_draws():
    draws = lottery_service.get_all_draws()
    """Получить все розыгрыши"""
    try:
        draws = lottery_service.get_all_draws()
        tickets = lottery_service.get_user_tickets()
        
        # Добавляем счетчик билетов для каждого розыгрыша
        for draw in draws:
            draw['tickets_count'] = len([t for t in tickets if t.get('draw_id') == draw['id']])
            draw['currency'] = 'COINS'
            
            # Форматирование времени для отображения
            if draw.get('date') and draw.get('time'):
                draw['time_left'] = f"{draw['date']} {draw['time']}"
        
        return jsonify(draws)
    except Exception as e:
        logger.error(f"Ошибка получения розыгрышей: {e}")
        return jsonify([]), 500

@admin_bp.route('/draws', methods=['POST'])
def add_draw():
    """Добавить новый розыгрыш"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные",
                "code": "NO_DATA"
            }), 400
        
        # Добавляем розыгрыш через сервис
        new_draw = lottery_service.add_draw(data)
        
        if new_draw:
            return jsonify({
                "success": True,
                "draw": new_draw,
                "message": "Розыгрыш добавлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Не все обязательные поля заполнены",
                "code": "MISSING_FIELDS"
            }), 400
        
    except Exception as e:
        logger.error(f"Ошибка добавления розыгрыша: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@admin_bp.route('/draws/<int:draw_id>', methods=['PUT'])
def update_draw(draw_id):
    """Обновить розыгрыш"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные",
                "code": "NO_DATA"
            }), 400
        
        # Обновляем розыгрыш через сервис
        updated_draw = lottery_service.update_draw(draw_id, data)
        
        if updated_draw:
            return jsonify({
                "success": True,
                "draw": updated_draw,
                "message": "Розыгрыш обновлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден",
                "code": "DRAW_NOT_FOUND"
            }), 404
        
    except Exception as e:
        logger.error(f"Ошибка обновления розыгрыша {draw_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@admin_bp.route('/draws/<int:draw_id>', methods=['DELETE'])
def delete_draw(draw_id):
    """Удалить розыгрыш"""
    try:
        # Удаляем розыгрыш через сервис
        success = lottery_service.delete_draw(draw_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Розыгрыш удален"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Розыгрыш не найден или имеет купленные билеты",
                "code": "DELETE_ERROR"
            }), 400
        
    except Exception as e:
        logger.error(f"Ошибка удаления розыгрыша {draw_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

# ========= УПРАВЛЕНИЕ ПАКЕТАМИ =========

@admin_bp.route('/packages', methods=['GET'])
def get_packages():
    """Получить все пакеты"""
    try:
        packages = lottery_service.get_packages()
        return jsonify(packages)
    except Exception as e:
        logger.error(f"Ошибка получения пакетов: {e}")
        return jsonify([]), 500

@admin_bp.route('/packages', methods=['POST'])
def add_package():
    """Добавить новый пакет"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные",
                "code": "NO_DATA"
            }), 400
        
        # Добавляем пакет через сервис
        package = lottery_service.add_package(data)
        
        if package:
            return jsonify({
                "success": True,
                "package": package,
                "message": "Пакет добавлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Не все обязательные поля заполнены",
                "code": "MISSING_FIELDS"
            }), 400
        
    except Exception as e:
        logger.error(f"Ошибка добавления пакета: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@admin_bp.route('/packages/<int:package_id>', methods=['PUT'])
def update_package(package_id):
    """Обновить пакет"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные",
                "code": "NO_DATA"
            }), 400
        
        # Обновляем пакет через сервис
        package = lottery_service.update_package(package_id, data)
        
        if package:
            return jsonify({
                "success": True,
                "package": package,
                "message": "Пакет обновлен"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Пакет не найден или ошибка обновления",
                "code": "UPDATE_ERROR"
            }), 404
        
    except Exception as e:
        logger.error(f"Ошибка обновления пакета {package_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

@admin_bp.route('/packages/<int:package_id>', methods=['DELETE'])
def delete_package(package_id):
    """Удалить пакет"""
    try:
        # Удаляем пакет через сервис
        success = lottery_service.delete_package(package_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Пакет удален"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Пакет не найден или ошибка удаления",
                "code": "DELETE_ERROR"
            }), 404
        
    except Exception as e:
        logger.error(f"Ошибка удаления пакета {package_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Внутренняя ошибка сервера",
            "code": "INTERNAL_ERROR"
        }), 500

# ========= СТАТИСТИКА =========

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Получить общую статистику"""
    try:
        stats = lottery_service.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Ошибка получения статистики: {e}")
        return jsonify({
            'total_draws': 0,
            'active_draws': 0,
            'completed_draws': 0,
            'total_packages': 0,
            'current_balance': 0,
            'total_tickets': 0,
            'winning_tickets': 0,
            'pending_tickets': 0
        }), 500