import pytest
import pandas as pd
from datetime import datetime
from src.etl_processor import ETLProcessor
from src.config import Config

@pytest.fixture
def sample_data():
    """Фикстура с тестовыми данными"""
    stores = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['Store_A', 'Store_B', 'Store_C', 'Store_D'],
        'city': ['Moscow', 'Moscow', 'SPb', 'SPb']
    })
    
    users = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['User1', 'User2', 'User3', 'User4'],
        'phone': ['+7911', '+7912', '+7913', '+7914'],
        'created_at': [
            datetime(2025, 1, 1),  # 2025 год - должен учитываться
            datetime(2024, 1, 1),  # 2024 год - не должен учитываться
            datetime(2025, 6, 1),  # 2025 год - должен учитываться
            datetime(2026, 1, 1)   # 2026 год - не должен учитываться
        ]
    })
    
    orders = pd.DataFrame({
        'id': [1, 2, 3, 4, 5, 6],
        'user_id': [1, 1, 3, 3, 2, 4],  # Только user_id 1 и 3 из 2025 года
        'store_id': [1, 2, 1, 2, 3, 4],
        'status': ['completed'] * 6,
        'amount': [100, 200, 300, 400, 500, 600],  # 500 и 600 не должны учитываться
        'created_at': [datetime(2025, 1, 1)] * 6
    })
    
    return stores, users, orders

def test_transform_logic(sample_data):
    """Тест логики трансформации"""
    config = Config()
    etl = ETLProcessor(config)
    
    stores_df, users_df, orders_df = sample_data
    result = etl.transform(stores_df, orders_df, users_df)
    
    # Проверяем что получили правильное количество строк
    # Москва: Store_A (100+300=400), Store_B (200+400=600)
    # SPb: Store_C (0), Store_D (0) - но у пользователей из 2025 нет заказов в этих магазинах
    assert len(result) == 2  # Только Moscow магазины
    
    # Проверяем суммы
    moscow_stores = result[result['city'] == 'Moscow']
    assert len(moscow_stores) == 2
    
    # Store_B должен быть первым (сумма 600)
    assert moscow_stores.iloc[0]['store_name'] == 'Store_B'
    assert moscow_stores.iloc[0]['target_amount'] == 600
    
    # Store_A должен быть вторым (сумма 400)
    assert moscow_stores.iloc[1]['store_name'] == 'Store_A'
    assert moscow_stores.iloc[1]['target_amount'] == 400

def test_top_3_per_city():
    """Тест ограничения топ-3 на город"""
    config = Config()
    etl = ETLProcessor(config)
    
    # Создаем тестовые данные с 5 магазинами в одном городе
    stores = pd.DataFrame({
        'id': range(1, 6),
        'name': [f'Store_{i}' for i in range(1, 6)],
        'city': ['Moscow'] * 5
    })
    
    users = pd.DataFrame({
        'id': [1],
        'name': ['Test'],
        'phone': ['+7911'],
        'created_at': [datetime(2025, 1, 1)]
    })
    
    # Каждому магазину разное количество заказов
    orders_data = []
    order_id = 1
    for store_id in range(1, 6):
        for amount in range(store_id * 100, store_id * 100 + 100, 10):
            orders_data.append({
                'id': order_id,
                'user_id': 1,
                'store_id': store_id,
                'status': 'completed',
                'amount': amount,
                'created_at': datetime(2025, 1, 1)
            })
            order_id += 1
    
    orders = pd.DataFrame(orders_data)
    
    result = etl.transform(stores, users, orders)
    
    # Должны получить только топ-3 магазина для Moscow
    assert len(result) == 3
    assert all(result['city'] == 'Moscow')