from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    id_task: Optional[int] = None

    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON"""
        return {
            "id": self.id,
            "username": self.username,
            "date": self.date,
            "id_task": self.id_task
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Создание объекта из словаря"""
        return cls(
            id=data.get("id", 0),
            username=data.get("username", ""),
            date=data.get("date", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            id_task=data.get("id_task", None)
        )

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', date='{self.date}', id_task={self.id_task})"