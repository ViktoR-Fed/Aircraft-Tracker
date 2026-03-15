from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAPI(ABC):
    """Абстрактный базовый класс для работы с API"""

    @abstractmethod
    def _connect(self, url: str) -> Optional[Dict[str, Any]]:
        """Приватный метод для подключения к API"""
        pass

    @abstractmethod
    def get_country_coordinates(self, country_name: str) -> Optional[List[str]]:
        """Получение географических координат страны"""
        pass

    @abstractmethod
    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        """Получение информации о самолетах в воздушном пространстве страны"""
        pass
