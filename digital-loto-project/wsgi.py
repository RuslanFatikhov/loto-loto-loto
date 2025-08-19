"""
WSGI entry point for production deployment
"""
import os
from app import create_app

# Создаем приложение для продакшн
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
