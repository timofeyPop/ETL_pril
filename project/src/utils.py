import logging
import tempfile
from minio import Minio
from minio.error import S3Error
import pandas as pd
import os

class MinioClient:
    """Клиент для работы с MinIO"""
    
    def __init__(self, config):
        self.client = Minio(
            config.MINIO_ENDPOINT,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            secure=config.USE_TLS
        )
        self.config = config
        
    def ensure_buckets(self):
        """Создание бакетов если они не существуют"""
        buckets = [self.config.INPUT_BUCKET, self.config.OUTPUT_BUCKET]
        for bucket in buckets:
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    print(f"Bucket '{bucket}' created")
            except Exception as e:
                print(f"Error creating bucket {bucket}: {e}")
    
    def read_parquet(self, bucket: str, object_name: str) -> pd.DataFrame:
        """Чтение Parquet файла из MinIO"""
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
                temp_file = tmp.name
            
            # Скачиваем файл
            self.client.fget_object(bucket, object_name, temp_file)
            print(f"Downloaded {object_name} from {bucket}")
            
            # Читаем в DataFrame
            df = pd.read_parquet(temp_file)
            
            # Удаляем временный файл
            os.unlink(temp_file)
            
            return df
            
        except Exception as e:
            print(f"Error reading {object_name}: {e}")
            raise
    
    def write_parquet(self, df: pd.DataFrame, bucket: str, object_name: str):
        """Запись DataFrame в Parquet в MinIO"""
        try:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as tmp:
                temp_file = tmp.name
            
            # Записываем DataFrame в Parquet
            df.to_parquet(temp_file, index=False)
            
            # Загружаем в MinIO
            self.client.fput_object(bucket, object_name, temp_file)
            print(f"Uploaded {object_name} to {bucket}")
            
            # Удаляем временный файл
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"Error writing {object_name}: {e}")
            raise