# lib/include/Ans.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class Ans:
    id: int
    id_task: int
    error_count: int = 0
    error_msg: List[str] = field(default_factory=list)
    code: str = ""
    date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def to_dict(self) -> dict:
        """Преобразование в словарь для JSON"""
        return {
            "id": self.id,
            "id_task": self.id_task,
            "error_count": self.error_count,
            "error_msg": self.error_msg,
            "code": self.code,
            "date": self.date
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Ans':
        """Создание объекта из словаря"""
        return cls(
            id=data.get("id", 0),
            id_task=data.get("id_task", 0),
            error_count=data.get("error_count", 0),
            error_msg=data.get("error_msg", []),
            code=data.get("code", ""),
            date=data.get("date", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )

    def __repr__(self):
        return (f"Ans(id={self.id}, id_task={self.id_task}, "
                f"error_count={self.error_count}, code='{self.code}')")
