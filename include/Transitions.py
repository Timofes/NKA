from typing import Dict
from dataclasses import dataclass


@dataclass
class Transition:
    StartQ: str
    V: str
    EndQ: str

    def to_dict(self) -> Dict:
        return {
            "StartQ": self.StartQ,
            "V": self.V,
            "EndQ": self.EndQ
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Transition':
        """Создание из словаря"""
        return cls(
            StartQ=str(data.get("StartQ", "")),
            V=str(data.get("V", "")),
            EndQ=str(data.get("EndQ", ""))
        )

    def __repr__(self):
        return f"{self.StartQ} --{self.V}--> {self.EndQ}"