from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Store:
    """Модель магазина"""
    id: int
    name: str
    city: str
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            city=data.get('city')
        )

@dataclass
class User:
    """Модель пользователя"""
    id: int
    name: str
    phone: str
    created_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict):
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            phone=data.get('phone'),
            created_at=created_at
        )

@dataclass
class Order:
    """Модель заказа"""
    id: int
    user_id: int
    store_id: int
    status: str
    amount: float
    created_at: datetime
    
    @classmethod
    def from_dict(cls, data: dict):
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            store_id=data.get('store_id'),
            status=data.get('status'),
            amount=float(data.get('amount', 0)),
            created_at=created_at
        )

@dataclass
class Result:
    """Модель результата"""
    city: str
    store_name: str
    target_amount: float
    
    def to_dict(self):
        return {
            'city': self.city,
            'store_name': self.store_name,
            'target_amount': round(self.target_amount, 2)
        }