import os

class Config:
    """Конфигурация приложения"""
    def __init__(self):
        self.MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.INPUT_BUCKET = os.getenv("INPUT_BUCKET", "input-data")
        self.OUTPUT_BUCKET = os.getenv("OUTPUT_BUCKET", "output-data")
        self.USE_TLS = False