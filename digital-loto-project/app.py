"""
Главный файл Flask приложения для цифрового лото
"""
import sys
import os
from flask import Flask, render_template, request, jsonify
import logging

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импорты наших модулей
try:
   from config import SECRET_KEY, DEBUG, HOST, PORT, setup_logging
   from models.data_manager import DataManager
   from routes.web_routes import web_bp
   from routes.api_routes import api_bp
   from routes.admin_routes import admin_bp
except ImportError as e:
   print(f"Ошибка импорта: {e}")
   print("Убедитесь, что все файлы созданы правильно")
   sys.exit(1)

# Настройка логирования
logger = setup_logging()

def create_app():
   """Фабрика приложения"""
   app = Flask(__name__)
   app.config['SECRET_KEY'] = SECRET_KEY
   
   # Регистрируем Blueprint'ы
   app.register_blueprint(web_bp)
   app.register_blueprint(api_bp)
   app.register_blueprint(admin_bp)
   
   # ПРОВЕРКА ЗАРЕГИСТРИРОВАННЫХ МАРШРУТОВ
   print("=== ЗАРЕГИСТРИРОВАННЫЕ МАРШРУТЫ ===")
   for rule in app.url_map.iter_rules():
       print(f"{rule.endpoint}: {rule.rule}")
   print("===================================")
   
   # Обработчики ошибок
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
           try:
               return render_template('404.html'), 404
           except:
               return "Страница не найдена", 404

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
           try:
               return render_template('500.html'), 500
           except:
               return "Внутренняя ошибка сервера", 500

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
   
   return app

def main():
   """Главная функция запуска приложения"""
   print("Инициализация приложения...")
   
   # Инициализируем данные при запуске
   try:
       DataManager.init_data_files()
       print("Файлы данных инициализированы")
   except Exception as e:
       print(f"Ошибка инициализации данных: {e}")
       return
   
   # Создаем приложение
   try:
       app = create_app()
       print("Приложение создано успешно")
   except Exception as e:
       print(f"Ошибка создания приложения: {e}")
       return
   
   # Запускаем приложение
   logger.info("Запуск приложения Flask для цифрового Лото с админ-панелью")
   print(f"Запуск сервера на http://{HOST}:{PORT}")
   print("Нажмите Ctrl+C для остановки")
   
   try:
       app.run(debug=DEBUG, host=HOST, port=PORT)
   except Exception as e:
       print(f"Ошибка запуска сервера: {e}")

if __name__ == '__main__':
   main()