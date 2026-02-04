import pandas as pd
from datetime import datetime
import logging

class ETLProcessor:
    """Основной процессор ETL"""
    
    def __init__(self, config):
        self.config = config
        from src.utils import MinioClient
        self.minio_client = MinioClient(config)
        
    def extract(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Извлечение данных из MinIO"""
        print("Starting data extraction...")
        
        stores_df = self.minio_client.read_parquet(
            self.config.INPUT_BUCKET, "stores.parquet"
        )
        orders_df = self.minio_client.read_parquet(
            self.config.INPUT_BUCKET, "orders.parquet"
        )
        users_df = self.minio_client.read_parquet(
            self.config.INPUT_BUCKET, "users.parquet"
        )
        
        print(f"Extracted: {len(stores_df)} stores, {len(orders_df)} orders, {len(users_df)} users")
        return stores_df, orders_df, users_df
    
    def transform(self, stores_df: pd.DataFrame, 
                  orders_df: pd.DataFrame, 
                  users_df: pd.DataFrame) -> pd.DataFrame:
        """Трансформация данных с использованием pandas"""
        print("Starting data transformation...")
        
        # Преобразуем даты если они строки
        if pd.api.types.is_string_dtype(users_df['created_at']):
            users_df['created_at'] = pd.to_datetime(users_df['created_at'])
        
        # Фильтруем пользователей 2025 года
        users_2025 = users_df[users_df['created_at'].dt.year == 2025].copy()
        print(f"Users from 2025: {len(users_2025)}")
        
        if len(users_2025) == 0:
            print("No users from 2025 found")
            return pd.DataFrame(columns=['city', 'store_name', 'target_amount'])
        
        # Объединяем заказы с пользователями 2025
        orders_filtered = orders_df.merge(
            users_2025[['id']], 
            left_on='user_id', 
            right_on='id',
            how='inner'
        )
        print(f"Orders from 2025 users: {len(orders_filtered)}")
        
        # Объединяем с магазинами
        merged = orders_filtered.merge(
            stores_df[['id', 'name', 'city']],
            left_on='store_id',
            right_on='id',
            how='inner',
            suffixes=('_order', '_store')
        )
        
        if len(merged) == 0:
            print("No orders from 2025 users found")
            return pd.DataFrame(columns=['city', 'store_name', 'target_amount'])
        
        # Группируем по городу и магазину, считаем сумму
        grouped = merged.groupby(['city', 'name']).agg(
            target_amount=('amount', 'sum')
        ).reset_index()
        
        # Сортируем и берем топ-3 для каждого города
        grouped['rank'] = grouped.groupby('city')['target_amount'].rank(
            method='dense', 
            ascending=False
        )
        
        result = grouped[grouped['rank'] <= 3].copy()
        result = result.sort_values(['city', 'target_amount'], ascending=[True, False])
        result = result.drop('rank', axis=1)
        result = result.rename(columns={'name': 'store_name'})
        
        print(f"Transformed data: {len(result)} rows")
        return result[['city', 'store_name', 'target_amount']]
    
    def load(self, result_df: pd.DataFrame):
        """Загрузка результата в MinIO"""
        print("Loading results to MinIO...")
        
        # Создаем имя файла с timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"result_{timestamp}.parquet"
        
        self.minio_client.write_parquet(
            result_df, 
            self.config.OUTPUT_BUCKET, 
            output_file
        )
        
        # Также сохраняем как result.parquet для удобства
        self.minio_client.write_parquet(
            result_df,
            self.config.OUTPUT_BUCKET,
            "result.parquet"
        )
        
        print(f"Results saved to {output_file} and result.parquet")
    
    def run(self):
        """Запуск всего ETL процесса"""
        start_time = datetime.now()
        print(f"ETL process started at {start_time}")
        
        try:
            # Создаем бакеты если нужно
            self.minio_client.ensure_buckets()
            
            # ETL процесс
            stores_df, orders_df, users_df = self.extract()
            result_df = self.transform(stores_df, orders_df, users_df)
            self.load(result_df)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"ETL process completed in {duration:.2f} seconds")
            print(f"Processed {len(result_df)} result rows")
            
            # Выводим результат для наглядности
            print("\nResults preview:")
            print(result_df.head(10).to_string())
            
        except Exception as e:
            print(f"ETL process failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise