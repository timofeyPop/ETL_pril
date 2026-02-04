import sys
import os
import time
from datetime import datetime

# Добавляем путь к src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Основная функция запуска приложения"""
    print(f"Starting ETL Application at {datetime.now()}")
    
    try:
        # Импортируем здесь, чтобы видеть ошибки импорта
        from src.etl_processor import ETLProcessor
        from src.config import Config
        
        # Инициализация конфигурации
        config = Config()
        
        # Запуск ETL процесса
        etl = ETLProcessor(config)
        etl.run()
        
        print(f"ETL Application completed successfully at {datetime.now()}")
        
    except Exception as e:
        print(f"Application failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()