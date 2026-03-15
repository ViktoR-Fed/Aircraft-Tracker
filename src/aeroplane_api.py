from typing import Any, Dict, List, Optional, Tuple

import requests

from src.abstract_class import BaseAPI


class AeroplaneAPI(BaseAPI):
    """
    Класс для работы с API nominatim.openstreetmap.org и opensky-network.org
    """

    nominatim_url = "https://nominatim.openstreetmap.org/search"
    opensky_url = "https://opensky-network.org/api/states/all"
    user_agent = "AeroplaneTracker/1.0"

    def init(self):
        self._nominatim_url = "https://nominatim.openstreetmap.org/search"
        self._opensky_url = "https://opensky-network.org/api/states/all"
        self._user_agent = "AeroplaneTracker/1.0"

    def _connect(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Приватный метод для подключения к API

        Args:
            url: URL для запроса
            params: Параметры запроса

        Returns:
            Ответ API в виде словаря или None в случае ошибки
        """
        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка подключения к API. Статус код: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при подключении к API: {e}")
            return None

    def get_country_coordinates(self, country_name: str) -> Optional[List[str]]:
        """
        Получение географических координат страны

        Args:
            country_name: Название страны

        Returns:
            Список координат [южная, северная, западная, восточная] или None
        """
        params = {"q": country_name, "format": "json", "limit": 1}

        response = self._connect(self.nominatim_url, params)

        if response and len(response) > 0:
            boundingbox = response[0].get("boundingbox")
            if boundingbox:
                return boundingbox

        print(f"Не удалось получить координаты для страны: {country_name}")
        return None

    def _get_bounding_box(self, coordinates: List[str]) -> Tuple[float, float, float, float]:
        """
        Преобразование координат в формат для OpenSky API

        Args:
            coordinates: Список координат [южная, северная, западная, восточная]

        Returns:
            Кортеж (ymin, xmin, ymax, xmax)
        """
        south, north, west, east = map(float, coordinates)
        return (south, west, north, east)

    def get_aeroplanes(self, country_name: str) -> List[Dict[str, Any]]:
        """
        Получение информации о самолетах в воздушном пространстве страны

        Args:
            country_name: Название страны

        Returns:
            Список словарей с информацией о самолетах
        """
        coordinates = self.get_country_coordinates(country_name)

        if not coordinates:
            return []

        south, west, north, east = self._get_bounding_box(coordinates)

        params = {"lamin": south, "lomin": west, "lamax": north, "lomax": east}

        response = self._connect(self.opensky_url, params)

        if response and "states" in response and response["states"]:
            return self._parse_aeroplane_data(response["states"])

        return []

    def _parse_aeroplane_data(self, states: List[List[Any]]) -> List[Dict[str, Any]]:
        """
        Парсинг данных о самолетах из ответа OpenSky API

        Args:
            states: Список состояний самолетов

        Returns:
            Список словарей с обработанными данными
        """
        aeroplanes = []

        for state in states:
            if len(state) >= 17:  # Проверка наличия всех полей
                aeroplane = {
                    "icao24": state[0],  # Уникальный идентификатор
                    "callsign": state[1],  # Позывной
                    "origin_country": state[2],  # Страна регистрации
                    "time_position": state[3],  # Время последнего обновления позиции
                    "last_contact": state[4],  # Время последнего контакта
                    "longitude": state[5],  # Долгота
                    "latitude": state[6],  # Широта
                    "baro_altitude": state[7],  # Высота (барометрическая)
                    "on_ground": state[8],  # На земле
                    "velocity": state[9],  # Скорость
                    "true_track": state[10],  # Направление
                    "vertical_rate": state[11],  # Вертикальная скорость
                    "sensors": state[12],  # Датчики
                    "geo_altitude": state[13],  # Географическая высота
                    "squawk": state[14],  # Код squawk
                    "spi": state[15],  # Indicates special purpose indicator
                    "position_source": state[16],  # Источник позиции
                }
                aeroplanes.append(aeroplane)

        return aeroplanes
