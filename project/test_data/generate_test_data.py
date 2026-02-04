import pandas as pd
import numpy as np
from datetime import datetime
import os

def create_simple_data():
    """Создание минимальных тестовых данных"""
    print("Creating simple test data...")
    
    # 1. Магазины
    stores = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Московский_1', 'Московский_2', 'Питерский_1', 'Питерский_2', 'Новосибирский'],
        'city': ['Moscow', 'Moscow', 'Saint Petersburg', 'Saint Petersburg', 'Novosibirsk']
    })
    
    # 2. Пользователи (половина из 2025 года)
    users = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': [f'User_{i}' for i in range(1, 11)],
        'phone': [f'+7912{i:07d}' for i in range(10)],
        'created_at': [
            datetime(2025, 1, 15),  # 2025 - учитывается
            datetime(2025, 3, 20),  # 2025 - учитывается
            datetime(2025, 6, 10),  # 2025 - учитывается
            datetime(2025, 8, 5),   # 2025 - учитывается
            datetime(2025, 11, 30), # 2025 - учитывается
            datetime(2024, 2, 15),  # 2024 - не учитывается
            datetime(2024, 5, 20),  # 2024 - не учитывается
            datetime(2026, 1, 10),  # 2026 - не учитывается
            datetime(2026, 3, 25),  # 2026 - не учитывается
            datetime(2026, 7, 15)   # 2026 - не учитывается
        ]
    })
    
    # 3. Заказы (только от пользователей 2025 года)
    orders_data = []
    order_id = 1
    
    # Московские магазины получают больше заказов
    for _ in range(10):  # Заказы для Москвы
        orders_data.append({
            'id': order_id,
            'user_id': np.random.choice([1, 2, 3, 4, 5]),  # только пользователи 2025
            'store_id': 1,  # Московский_1
            'status': 'completed',
            'amount': np.random.uniform(1000, 5000),
            'created_at': datetime(2025, np.random.randint(1, 13), np.random.randint(1, 29))
        })
        order_id += 1
        
        orders_data.append({
            'id': order_id,
            'user_id': np.random.choice([1, 2, 3, 4, 5]),
            'store_id': 2,  # Московский_2
            'status': 'completed',
            'amount': np.random.uniform(800, 4000),
            'created_at': datetime(2025, np.random.randint(1, 13), np.random.randint(1, 29))
        })
        order_id += 1
    
    # Питерские магазины
    for _ in range(5):
        orders_data.append({
            'id': order_id,
            'user_id': np.random.choice([1, 2, 3, 4, 5]),
            'store_id': 3,  # Питерский_1
            'status': 'completed',
            'amount': np.random.uniform(1500, 4500),
            'created_at': datetime(2025, np.random.randint(1, 13), np.random.randint(1, 29))
        })
        order_id += 1
        
        orders_data.append({
            'id': order_id,
            'user_id': np.random.choice([1, 2, 3, 4, 5]),
            'store_id': 4,  # Питерский_2
            'status': 'completed',
            'amount': np.random.uniform(1000, 3000),
            'created_at': datetime(2025, np.random.randint(1, 13), np.random.randint(1, 29))
        })
        order_id += 1
    
    # Новосибирский магазин
    for _ in range(3):
        orders_data.append({
            'id': order_id,
            'user_id': np.random.choice([1, 2, 3, 4, 5]),
            'store_id': 5,  # Новосибирский
            'status': 'completed',
            'amount': np.random.uniform(500, 2000),
            'created_at': datetime(2025, np.random.randint(1, 13), np.random.randint(1, 29))
        })
        order_id += 1
    
    orders = pd.DataFrame(orders_data)
    
    return stores, users, orders

def generate_simple_test_data():
    """Генерация и сохранение тестовых данных"""
    stores, users, orders = create_simple_data()
    
    # Создаем папку если нет
    os.makedirs('test_data', exist_ok=True)
    
    # Сохраняем в Parquet
    stores.to_parquet('test_data/stores.parquet', index=False)
    users.to_parquet('test_data/users.parquet', index=False)
    orders.to_parquet('test_data/orders.parquet', index=False)
    
    print(f"Created test_data/stores.parquet: {len(stores)} rows")
    print(f"Created test_data/users.parquet: {len(users)} rows")
    print(f"Created test_data/orders.parquet: {len(orders)} rows")
    
    # Показываем ожидаемый результат
    print("\n=== Expected Analysis ===")
    print("Users from 2025:", len(users[users['created_at'].dt.year == 2025]))
    print("Total orders:", len(orders))
    
    # Рассчитываем вручную
    users_2025 = users[users['created_at'].dt.year == 2025]
    orders_filtered = orders[orders['user_id'].isin(users_2025['id'])]
    
    merged = pd.merge(orders_filtered, stores, left_on='store_id', right_on='id')
    result = merged.groupby(['city', 'name']).agg({'amount': 'sum'}).reset_index()
    result = result.rename(columns={'name': 'store_name', 'amount': 'target_amount'})
    result = result.sort_values(['city', 'target_amount'], ascending=[True, False])
    
    print("\nExpected top stores per city:")
    for city in ['Moscow', 'Saint Petersburg', 'Novosibirsk']:
        city_results = result[result['city'] == city].head(3)
        print(f"\n{city}:")
        for _, row in city_results.iterrows():
            print(f"  {row['store_name']}: ${row['target_amount']:.2f}")
    
    return True

if __name__ == "__main__":
    generate_simple_test_data()