import os
import sys
import time

# Добавляем путь
sys.path.append('/app')

def upload_test_data():
    """Загрузка тестовых данных в MinIO"""
    print("=== Uploading test data to MinIO ===")
    
    try:
        from src.config import Config
        from src.utils import MinioClient
        import pandas as pd
        
        config = Config()
        print(f"Config: {config.MINIO_ENDPOINT}, bucket: {config.INPUT_BUCKET}")
        
        minio_client = MinioClient(config)
        
        # Создаем бакеты
        print("Creating buckets...")
        minio_client.ensure_buckets()
        
        # Загружаем данные
        files = ['stores.parquet', 'orders.parquet', 'users.parquet']
        
        for file in files:
            file_path = f"/app/test_data/{file}"
            print(f"\nProcessing {file}...")
            
            if os.path.exists(file_path):
                try:
                    # Проверяем размер файла
                    file_size = os.path.getsize(file_path)
                    print(f"  File size: {file_size} bytes")
                    
                    if file_size == 0:
                        print(f"  WARNING: {file} is empty!")
                        continue
                    
                    # Читаем файл
                    df = pd.read_parquet(file_path)
                    print(f"  Loaded: {len(df)} rows, {len(df.columns)} columns")
                    
                    # Загружаем в MinIO
                    minio_client.write_parquet(df, config.INPUT_BUCKET, file)
                    print(f"  ✓ Uploaded to MinIO")
                    
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"  ✗ File not found: {file_path}")
        
        print("\n=== Upload completed ===")
        return True
        
    except Exception as e:
        print(f"=== Fatal error: {str(e)} ===")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Ждем MinIO
    time.sleep(5)
    success = upload_test_data()
    sys.exit(0 if success else 1)