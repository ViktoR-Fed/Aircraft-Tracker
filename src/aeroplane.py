from typing import Any, Dict, List, Optional, Union

from src.validators import Validators


class Aeroplane:
    """
    Класс для работы с информацией о самолетах
    """

    slots = [
        "_callsign",
        "_origin_country",
        "_velocity",
        "_baro_altitude",
        "_on_ground",
        "_longitude",
        "_latitude",
        "_icao24",
    ]

    def init(
        self,
        callsign: str,
        origin_country: str,
        velocity: Optional[float],
        baro_altitude: Optional[float],
        on_ground: bool = False,
        longitude: Optional[float] = None,
        latitude: Optional[float] = None,
        icao24: Optional[str] = None,
    ):
        """
        Инициализация объекта самолета

        Args:
            callsign: Позывной самолета
            origin_country: Страна регистрации
            velocity: Скорость полета (м/с)
            baro_altitude: Барометрическая высота (м)
            on_ground: Находится ли на земле
            longitude: Долгота
            latitude: Широта
            icao24: Уникальный идентификатор
        """
        self._callsign = self._validate_callsign(callsign)
        self._origin_country = self._validate_origin_country(origin_country)
        self._velocity = self._validate_velocity(velocity)
        self._baro_altitude = self._validate_altitude(baro_altitude)
        self._on_ground = self._validate_on_ground(on_ground)
        self._longitude = self._validate_longitude(longitude)
        self._latitude = self._validate_latitude(latitude)
        self._icao24 = self._validate_icao24(icao24)

    # Приватные методы валидации
    def _validate_callsign(self, callsign: str) -> str:
        """Валидация позывного"""
        if not Validators.validate_string(callsign):
            raise ValueError("Позывной должен быть непустой строкой")
        return callsign.strip()

    def _validate_origin_country(self, country: str) -> str:
        """Валидация страны регистрации"""
        if not Validators.validate_string(country):
            raise ValueError("Страна регистрации должна быть непустой строкой")
        return country.strip()

    def _validate_velocity(self, velocity: Optional[Union[float, int]]) -> Optional[float]:
        """Валидация скорости"""
        if velocity is None:
            return None
        return Validators.validate_positive_number(float(velocity), "Скорость")

    def _validate_altitude(self, altitude: Optional[Union[float, int]]) -> Optional[float]:
        """Валидация высоты"""
        if altitude is None:
            return None
        return Validators.validate_number(float(altitude), "Высота")

    def _validate_on_ground(self, on_ground: bool) -> bool:
        """Валидация флага нахождения на земле"""
        return Validators.validate_boolean(on_ground)

    def _validate_longitude(self, longitude: Optional[Union[float, int]]) -> Optional[float]:
        """Валидация долготы"""
        if longitude is None:
            return None
        return Validators.validate_longitude(float(longitude))

    def _validate_latitude(self, latitude: Optional[Union[float, int]]) -> Optional[float]:
        """Валидация широты"""
        if latitude is None:
            return None
        return Validators.validate_latitude(float(latitude))

    def _validate_icao24(self, icao24: Optional[str]) -> Optional[str]:
        """Валидация ICAO24 кода"""
        if icao24 is None:
            return None
        if not Validators.validate_string(icao24):
            raise ValueError("ICAO24 код должен быть строкой")
        return icao24.strip()

    # Геттеры для атрибутов
    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @property
    def velocity(self) -> Optional[float]:
        return self._velocity

    @property
    def baro_altitude(self) -> Optional[float]:
        return self._baro_altitude

    @property
    def on_ground(self) -> bool:
        return self._on_ground

    @property
    def longitude(self) -> Optional[float]:
        return self._longitude

    @property
    def latitude(self) -> Optional[float]:
        return self._latitude

    @property
    def icao24(self) -> Optional[str]:
        return self._icao24

    # Магические методы сравнения
    def eq(self, other: "Aeroplane") -> bool:
        """Сравнение на равенство по скорости и высоте"""
        if not isinstance(other, Aeroplane):
            return False
        return self.velocity == other.velocity and self.baro_altitude == other.baro_altitude

    def lt(self, other: "Aeroplane") -> bool:
        """Сравнение на меньше (по высоте)"""
        if not isinstance(other, Aeroplane):
            return NotImplemented

        if self.baro_altitude is None and other.baro_altitude is None:
            return False
        if self.baro_altitude is None:
            return True
        if other.baro_altitude is None:
            return False
        return self.baro_altitude < other.baro_altitude

    def le(self, other: "Aeroplane") -> bool:
        """Сравнение на меньше или равно (по высоте)"""
        return self < other or self == other

    def gt(self, other: "Aeroplane") -> bool:
        """Сравнение на больше (по высоте)"""
        return not (self <= other)

    def ge(self, other: "Aeroplane") -> bool:
        """Сравнение на больше или равно (по высоте)"""
        return not (self < other)

    # Методы сравнения по скорости
    def faster_than(self, other: "Aeroplane") -> bool:
        """Сравнение по скорости"""
        if not isinstance(other, Aeroplane):
            return NotImplemented

        if self.velocity is None and other.velocity is None:
            return False
        if self.velocity is None:
            return False
        if other.velocity is None:
            return True
        return self.velocity > other.velocity

    @classmethod
    def cast_to_object_list(cls, aeroplanes_data: List[Dict[str, Any]]) -> List["Aeroplane"]:
        """
        Преобразование списка словарей в список объектов Aeroplane

        Args:
            aeroplanes_data: Список словарей с данными о самолетах

        Returns:
            Список объектов Aeroplane
        """
        aeroplanes = []

        for data in aeroplanes_data:
            try:
                aeroplane = cls(
                    callsign=data.get("callsign", "Unknown"),
                    origin_country=data.get("origin_country", "Unknown"),
                    velocity=data.get("velocity"),
                    baro_altitude=data.get("baro_altitude"),
                    on_ground=data.get("on_ground", False),
                    longitude=data.get("longitude"),
                    latitude=data.get("latitude"),
                    icao24=data.get("icao24"),
                )
                aeroplanes.append(aeroplane)
            except (ValueError, TypeError) as e:
                print(f"Ошибка при создании объекта самолета: {e}")
                continue

        return aeroplanes

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование объекта в словарь"""
        return {
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "baro_altitude": self.baro_altitude,
            "on_ground": self.on_ground,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "icao24": self.icao24,
        }

    def str(self) -> str:
        """Строковое представление самолета"""
        return (
            f"Самолет {self.callsign} (Страна: {self.origin_country}, "
            f"Скорость: {self.velocity if self.velocity else 'N/A'} м/с, "
            f"Высота: {self.baro_altitude if self.baro_altitude else 'N/A'} м, "
            f"{'На земле' if self.on_ground else 'В воздухе'})"
        )
