from typing import Any, Union


class Validators:
    """Класс с методами валидации данных"""

    @staticmethod
    def validate_string(value: Any) -> bool:
        """Проверка, что значение является непустой строкой"""
        return isinstance(value, str) and value.strip() != ""

    @staticmethod
    def validate_number(value: Union[int, float], field_name: str) -> float:
        """Проверка, что значение является числом"""
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} должен быть числом")
        return float(value)

    @staticmethod
    def validate_positive_number(value: Union[int, float], field_name: str) -> float:
        """Проверка, что значение является положительным числом"""
        num = Validators.validate_number(value, field_name)
        if num < 0:
            raise ValueError(f"{field_name} должен быть неотрицательным")
        return num

    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """Проверка, что значение является булевым"""
        return bool(value)

    @staticmethod
    def validate_longitude(value: float) -> float:
        """Проверка корректности долготы"""
        if not -180 <= value <= 180:
            raise ValueError(f"Долгота должна быть в диапазоне [-180, 180], получено {value}")
        return value

    @staticmethod
    def validate_latitude(value: float) -> float:
        """Проверка корректности широты"""
        if not -90 <= value <= 90:
            raise ValueError(f"Широта должна быть в диапазоне [-90, 90], получено {value}")
        return value
