from abc import ABC, abstractmethod
from typing import List

from src.aeroplane import Aeroplane


class BaseStorage(ABC):
    """Абстрактный базовый класс для работы с хранилищем данных"""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """
        Добавление информации о самолете в хранилище

        Args:
            aeroplane: Объект самолета

        Returns:
            True в случае успеха, False в случае ошибки
        """
        pass

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> bool:
        """
        Добавление нескольких самолетов в хранилище

        Args:
            aeroplanes: Список объектов самолетов

        Returns:
            True в случае успеха, False в случае ошибки
        """
        pass

    @abstractmethod
    def get_aeroplanes(self, **criteria) -> List[Aeroplane]:
        """
        Получение данных из хранилища по указанным критериям

        Args:
            **criteria: Критерии фильтрации (по стране, по высоте и т.д.)

        Returns:
            Список объектов самолетов
        """
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """
        Удаление информации о самолете из хранилища

        Args:
            aeroplane: Объект самолета

        Returns:
            True в случае успеха, False в случае ошибки
        """
        pass

    @abstractmethod
    def delete_aeroplanes(self, **criteria) -> int:
        """
        Удаление самолетов по критериям

        Args:
            **criteria: Критерии для удаления

        Returns:
            Количество удаленных самолетов
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """
        Очистка хранилища

        Returns:
            True в случае успеха, False в случае ошибки
        """
        pass
