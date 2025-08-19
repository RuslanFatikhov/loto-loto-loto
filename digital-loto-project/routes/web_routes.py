"""
Веб-маршруты для отображения HTML страниц
"""
import logging
from flask import Blueprint, render_template, abort
from models.lottery import LotteryService
from models.data_manager import DataManager
from utils.helpers import TicketGrouping
from config import JSON_FILES
from flask import Blueprint, render_template, abort, redirect, url_for

logger = logging.getLogger(__name__)

# Создаем Blueprint для веб-маршрутов
web_bp = Blueprint('web', __name__)

# Инициализируем сервисы
lottery_service = LotteryService()
data_manager = DataManager()

@web_bp.route('/')
def index():
    """Главная страница"""
    try:
        draws = lottery_service.get_all_draws()
        banners_data = data_manager.load_json(JSON_FILES['banners'])
        balance = lottery_service.get_balance()
        
        # Безопасное извлечение данных
        banners = banners_data.get('banners', []) if isinstance(banners_data, dict) else []
        
        return render_template('index.html', 
                             draws=draws, 
                             banners=banners,
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки главной страницы: {e}")
        abort(500)

@web_bp.route('/tickets')
def tickets():
    """Страница "Мои билеты" с группировкой и фильтрами"""
    try:
        user_tickets = lottery_service.get_user_tickets()
        draws = lottery_service.get_all_draws()
        balance = lottery_service.get_balance()
        
        # Группируем билеты по розыгрышам
        grouped_tickets = TicketGrouping.group_tickets_by_draw(user_tickets, draws)
        
        # Получаем список розыгрышей для фильтра
        draw_filters = TicketGrouping.get_draws_for_filter(user_tickets, draws)
        
        return render_template('tickets.html', 
                             grouped_tickets=grouped_tickets,
                             draw_filters=draw_filters,
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки страницы билетов: {e}")
        abort(500)

@web_bp.route('/draw/<int:draw_id>')
def draw_detail(draw_id):
    """Страница конкретного розыгрыша"""
    try:
        draw = lottery_service.get_draw_by_id(draw_id)
        if not draw:
            abort(404)
        
        user_tickets = lottery_service.get_user_tickets(draw_id)
        balance = lottery_service.get_balance()
        
        return render_template('draw.html', 
                             draw=draw, 
                             tickets=user_tickets,
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки страницы розыгрыша {draw_id}: {e}")
        abort(500)

@web_bp.route('/admin')
def admin():
    """Админка"""
    try:
        draws = lottery_service.get_all_draws()
        packages = lottery_service.get_packages()
        tickets = lottery_service.get_user_tickets()
        balance = lottery_service.get_balance()
        
        # Добавляем статистику по билетам
        tickets_stats = lottery_service.calculate_tickets_stats()
        
        return render_template('admin.html', 
                             draws=draws, 
                             packages=packages,
                             tickets=tickets,
                             balance={'coins': balance},
                             **tickets_stats)
    except Exception as e:
        logger.error(f"Ошибка загрузки админки: {e}")
        abort(500)



@web_bp.route('/packages')
def packages():
    """Страница акции - пакеты билетов"""
    try:
        balance = lottery_service.get_balance()
        
        return render_template('packages.html',
                             balance=balance)
    except Exception as e:
        logger.error(f"Ошибка загрузки страницы пакетов: {e}")
        abort(500)


@web_bp.route('/buy_ticket/<int:draw_id>')
def buy_ticket(draw_id):
    """Страница покупки билета"""
    try:
        # Получаем данные розыгрыша
        draw = lottery_service.get_draw_by_id(draw_id)
        if not draw:
            logger.warning(f"Розыгрыш с ID {draw_id} не найден")
            abort(404)
        
        # Получаем баланс пользователя
        balance = lottery_service.get_balance()
        
        return render_template('ticket_purchase.html',
                             draw=draw,
                             balance=balance)
        
    except Exception as e:
        logger.error(f"Ошибка загрузки страницы покупки билета для розыгрыша {draw_id}: {e}")
        abort(500)

@web_bp.route('/buy_ticket')
def buy_ticket_redirect():
    """Редирект на главную если не указан ID розыгрыша"""
    logger.info("Попытка доступа к покупке билета без указания ID розыгрыша")
    return redirect(url_for('web.index'))