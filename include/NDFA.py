from typing import List, Dict, Optional
from dataclasses import dataclass, field
from lib.include.Transitions import Transition


@dataclass
class NDFA:
    V: List[str] = field(default_factory=list)              # Алфавит как массив
    Q: List[str] = field(default_factory=list)              # Состояния как массив
    q0: str = ""                                            # Начальное состояние
    Phi: List[Transition] = field(default_factory=list)     # Переходы как массив
    F: List[str] = field(default_factory=list)              # Конечные состояния как массив

    def _add_unique(self, lst: List[str], item: str) -> List[str]:
        """Добавляет элемент в массив, если его там еще нет"""
        if item not in lst:
            lst.append(item)
        return lst

    def _remove_item(self, lst: List[str], item: str) -> List[str]:
        """Удаляет элемент из массива"""
        if item in lst:
            lst.remove(item)
        return lst

    def set_alphabet(self, alphabet: List[str]) -> 'NDFA':
        """Установить алфавит"""
        self.V = alphabet
        return self

    def add_symbol(self, symbol: str) -> 'NDFA':
        """Добавить символ в алфавит (без дубликатов)"""
        self._add_unique(self.V, symbol)
        return self

    def remove_symbol(self, symbol: str) -> 'NDFA':
        """Удалить символ из алфавита"""
        self._remove_item(self.V, symbol)
        return self

    def set_states(self, states: List[str]) -> 'NDFA':
        """Установить множество состояний"""
        self.Q = states
        return self

    def add_state(self, state: str) -> 'NDFA':
        """Добавить состояние (без дубликатов)"""
        self._add_unique(self.Q, state)
        return self

    def remove_state(self, state: str) -> 'NDFA':
        """Удалить состояние"""
        self._remove_item(self.Q, state)
        self.Phi = [t for t in self.Phi if t.StartQ != state and t.EndQ != state]
        self._remove_item(self.F, state)
        if self.q0 == state:
            self.q0 = ""
        return self

    def set_initial_state(self, state: str) -> 'NDFA':
        """Установить начальное состояние"""
        self.q0 = state
        return self

    def set_final_states(self, states: List[str]) -> 'NDFA':
        """Установить конечные состояния"""
        self.F = states
        return self

    def add_final_state(self, state: str) -> 'NDFA':
        """Добавить конечное состояние (без дубликатов)"""
        self._add_unique(self.F, state)
        return self

    def remove_final_state(self, state: str) -> 'NDFA':
        """Удалить конечное состояние"""
        self._remove_item(self.F, state)
        return self

    def add_transition(self, start_q: str, v: str, end_q: str) -> 'NDFA':
        """Добавить переход"""
        transition = Transition(start_q, v, end_q)
        self.Phi.append(transition)
        return self

    def add_transitions(self, transitions: List[Transition]) -> 'NDFA':
        """Добавить несколько переходов"""
        self.Phi.extend(transitions)
        return self

    def remove_transition(self, start_q: str, v: str, end_q: str) -> 'NDFA':
        """Удалить конкретный переход"""
        self.Phi = [t for t in self.Phi
                    if not (t.StartQ == start_q and t.V == v and t.EndQ == end_q)]
        return self

    def remove_transitions_from(self, state: str) -> 'NDFA':
        """Удалить все переходы из состояния"""
        self.Phi = [t for t in self.Phi if t.StartQ != state]
        return self

    def remove_transitions_to(self, state: str) -> 'NDFA':
        """Удалить все переходы в состояние"""
        self.Phi = [t for t in self.Phi if t.EndQ != state]
        return self

    def get_transitions_from(self, state: str) -> List[Transition]:
        """Получить все переходы из состояния"""
        return [t for t in self.Phi if t.StartQ == state]

    def get_transitions_to(self, state: str) -> List[Transition]:
        """Получить все переходы в состояние"""
        return [t for t in self.Phi if t.EndQ == state]

    def clear(self) -> 'NDFA':
        """Очистить все данные"""
        self.V.clear()
        self.Q.clear()
        self.q0 = ""
        self.Phi.clear()
        self.F.clear()
        return self

    def to_dict(self) -> Dict:
        """Преобразование в словарь для JSON"""
        return {
            "V": sorted(self.V),  # Сортируем для читаемости
            "Q": sorted(self.Q),
            "q0": self.q0,
            "Phi": [transition.to_dict() for transition in self.Phi],
            "F": sorted(self.F)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'NDFA':
        """Создание объекта из словаря"""
        transitions = []
        for transition_data in data.get("Phi", []):
            transitions.append(Transition.from_dict(transition_data))

        return cls(
            V=list(data.get("V", [])),
            Q=list(data.get("Q", [])),
            q0=data.get("q0", ""),
            Phi=transitions,
            F=list(data.get("F", []))
        )

    def __repr__(self):
        return (f"NDFA(V={self.V}, Q={self.Q}, q0='{self.q0}', "
                f"Phi=[{len(self.Phi)} transitions], F={self.F})")

    def print_info(self):
        """Вывод информации об автомате"""
        print("═" * 50)
        print("ИНФОРМАЦИЯ О НКА:")
        print(f"Алфавит (V): {self.V}")
        print(f"Состояния (Q): {self.Q}")
        print(f"Начальное состояние (q0): '{self.q0}'")
        print(f"Конечные состояния (F): {self.F}")
        print(f"Количество переходов: {len(self.Phi)}")
        if self.Phi:
            print("Переходы (Phi):")
            for i, transition in enumerate(self.Phi, 1):
                print(f"  {i:2d}. {transition}")
        print(f"Корректность: {'✓' if self.is_valid() else '✗'}")
        print("═" * 50)