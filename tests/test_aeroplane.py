from typing import Any, Dict, List, Optional

import pytest

from src.aeroplane import Aeroplane
from src.validators import Validators


def create_test_aeroplane(
    callsign: str = "TEST123",
    origin_country: str = "Russia",
    velocity: Optional[float] = 250.0,
    baro_altitude: Optional[float] = 10000.0,
    on_ground: bool = False,
    longitude: Optional[float] = 37.62,
    latitude: Optional[float] = 55.75,
    icao24: Optional[str] = "abc123",
) -> Aeroplane:
    """Создание тестового самолета"""
    return Aeroplane(
        callsign=callsign,
        origin_country=origin_country,
        velocity=velocity,
        baro_altitude=baro_altitude,
        on_ground=on_ground,
        longitude=longitude,
        latitude=latitude,
        icao24=icao24,
    )


# Тесты инициализации и валидации
def test_init_valid_values():
    """Тест инициализации с корректными значениями"""

    aeroplane = create_test_aeroplane()

    assert aeroplane.callsign == "TEST123"
    assert aeroplane.origin_country == "Russia"
    assert aeroplane.velocity == 250.0
    assert aeroplane.baro_altitude == 10000.0
    assert aeroplane.on_ground == False
    assert aeroplane.longitude == 37.62
    assert aeroplane.latitude == 55.75
    assert aeroplane.icao24 == "abc123"


def test_init_with_none_values():
    """Тест инициализации с None значениями"""

    aeroplane = Aeroplane(
        callsign="TEST123",
        origin_country="Russia",
        velocity=None,
        baro_altitude=None,
        on_ground=False,
        longitude=None,
        latitude=None,
        icao24=None,
    )

    assert aeroplane.velocity is None
    assert aeroplane.baro_altitude is None
    assert aeroplane.longitude is None
    assert aeroplane.latitude is None
    assert aeroplane.icao24 is None


def test_validation_callsign():
    """Тест валидации позывного"""

    # Корректные значения
    aeroplane = create_test_aeroplane()
    aeroplane.callsign = "NEW123"
    assert aeroplane.callsign == "NEW123"

    aeroplane.callsign = "  SPACE123  "
    assert aeroplane.callsign == "SPACE123"

    # Некорректные значения
    try:
        aeroplane.callsign = ""
        assert False, "Должно быть исключение для пустой строки"
    except ValueError as e:
        assert "Позывной должен быть непустой строкой" in str(e)

    try:
        aeroplane.callsign = "   "
        assert False, "Должно быть исключение для строки из пробелов"
    except ValueError as e:
        assert "Позывной должен быть непустой строкой" in str(e)

    try:
        aeroplane.callsign = 123  # type: ignore
        assert False, "Должно быть исключение для числа"
    except ValueError as e:
        assert "Позывной должен быть непустой строкой" in str(e)


def test_validation_origin_country():
    """Тест валидации страны"""

    aeroplane = create_test_aeroplane()

    # Корректные значения
    aeroplane.origin_country = "USA"
    assert aeroplane.origin_country == "USA"

    aeroplane.origin_country = "  Germany  "
    assert aeroplane.origin_country == "Germany"

    # Некорректные значения
    try:
        aeroplane.origin_country = ""
        assert False, "Должно быть исключение для пустой строки"
    except ValueError as e:
        assert "Страна регистрации должна быть непустой строкой" in str(e)

    try:
        aeroplane.origin_country = "   "
        assert False, "Должно быть исключение для строки из пробелов"
    except ValueError as e:
        assert "Страна регистрации должна быть непустой строкой" in str(e)


def test_validation_coordinates():
    """Тест валидации координат"""

    aeroplane = create_test_aeroplane()

    # Корректные значения долготы
    aeroplane.longitude = 0
    assert aeroplane.longitude == 0.0

    aeroplane.longitude = 180
    assert aeroplane.longitude == 180.0

    aeroplane.longitude = -180
    assert aeroplane.longitude == -180.0

    aeroplane.longitude = None
    assert aeroplane.longitude is None

    # Некорректные значения долготы
    try:
        aeroplane.longitude = 181
        assert False, "Должно быть исключение для долготы > 180"
    except ValueError as e:
        assert "Долгота должна быть в диапазоне" in str(e)

    try:
        aeroplane.longitude = -181
        assert False, "Должно быть исключение для долготы < -180"
    except ValueError as e:
        assert "Долгота должна быть в диапазоне" in str(e)

    # Корректные значения широты
    aeroplane.latitude = 0
    assert aeroplane.latitude == 0.0

    aeroplane.latitude = 90
    assert aeroplane.latitude == 90.0

    aeroplane.latitude = -90
    assert aeroplane.latitude == -90.0

    aeroplane.latitude = None
    assert aeroplane.latitude is None

    # Некорректные значения широты
    try:
        aeroplane.latitude = 91
        assert False, "Должно быть исключение для широты > 90"
    except ValueError as e:
        assert "Широта должна быть в диапазоне" in str(e)

    try:
        aeroplane.latitude = -91
        assert False, "Должно быть исключение для широты < -90"
    except ValueError as e:
        assert "Широта должна быть в диапазоне" in str(e)


def test_validation_icao24():
    """Тест валидации ICAO24 кода"""

    aeroplane = create_test_aeroplane()

    # Корректные значения
    aeroplane.icao24 = "xyz789"
    assert aeroplane.icao24 == "xyz789"

    aeroplane.icao24 = "  abc123  "
    assert aeroplane.icao24 == "abc123"

    aeroplane.icao24 = None
    assert aeroplane.icao24 is None

    # Некорректные значения
    try:
        aeroplane.icao24 = ""
        assert False, "Должно быть исключение для пустой строки"
    except ValueError as e:
        assert "ICAO24 код должен быть строкой" in str(e)

    try:
        aeroplane.icao24 = "   "
        assert False, "Должно быть исключение для строки из пробелов"
    except ValueError as e:
        assert "ICAO24 код должен быть строкой" in str(e)


# Тесты методов сравнения
def test_equality_comparison():
    """Тест сравнения на равенство"""

    a1 = create_test_aeroplane(velocity=250, baro_altitude=10000)
    a2 = create_test_aeroplane(velocity=250, baro_altitude=10000)
    a3 = create_test_aeroplane(velocity=300, baro_altitude=10000)
    a4 = create_test_aeroplane(velocity=250, baro_altitude=15000)

    assert a1 == a2, "Одинаковые скорость и высота должны быть равны"
    assert a1 != a3, "Разная скорость - не равны"
    assert a1 != a4, "Разная высота - не равны"
    assert a1 != "not an aeroplane", "Сравнение с другим типом должно быть False"


def test_altitude_comparison():
    """Тест сравнения по высоте"""

    a1 = create_test_aeroplane(baro_altitude=10000)
    a2 = create_test_aeroplane(baro_altitude=15000)
    a3 = create_test_aeroplane(baro_altitude=10000)
    a4 = create_test_aeroplane(baro_altitude=None)

    # Меньше
    assert a1 < a2, "10000 < 15000"
    assert not (a2 < a1), "15000 не < 10000"
    assert not (a1 < a3), "10000 не < 10000"

    # Меньше или равно
    assert a1 <= a2, "10000 <= 15000"
    assert a1 <= a3, "10000 <= 10000"

    # Больше
    assert a2 > a1, "15000 > 10000"
    assert not (a1 > a2), "10000 не > 15000"

    # Больше или равно
    assert a2 >= a1, "15000 >= 10000"
    assert a1 >= a3, "10000 >= 10000"

    # Тесты с None
    assert a4 < a1, "None < 10000"
    assert not (a1 < a4), "10000 не < None"
    assert a4 <= a1, "None <= 10000"


def test_faster_than():
    """Тест сравнения по скорости"""

    a1 = create_test_aeroplane(velocity=250)
    a2 = create_test_aeroplane(velocity=300)
    a3 = create_test_aeroplane(velocity=250)
    a4 = create_test_aeroplane(velocity=None)
    a5 = create_test_aeroplane(velocity=None)

    assert a2.faster_than(a1), "300 быстрее 250"
    assert not a1.faster_than(a2), "250 не быстрее 300"
    assert not a1.faster_than(a3), "250 не быстрее 250"

    # Тесты с None
    assert a1.faster_than(a4), "250 быстрее None"
    assert not a4.faster_than(a1), "None не быстрее 250"
    assert not a4.faster_than(a5), "None не быстрее None"


# Тесты методов преобразования
def test_to_dict():
    """Тест преобразования в словарь"""

    aeroplane = create_test_aeroplane()
    result = aeroplane.to_dict()

    assert isinstance(result, dict)
    assert result["callsign"] == "TEST123"
    assert result["origin_country"] == "Russia"
    assert result["velocity"] == 250.0
    assert result["baro_altitude"] == 10000.0
    assert result["on_ground"] == False
    assert result["longitude"] == 37.62
    assert result["latitude"] == 55.75
    assert result["icao24"] == "abc123"


def test_cast_to_object_list():
    """Тест преобразования списка словарей в список объектов"""

    data = [
        {
            "callsign": "FLT1",
            "origin_country": "USA",
            "velocity": 300,
            "baro_altitude": 12000,
            "on_ground": False,
            "longitude": -73.98,
            "latitude": 40.75,
            "icao24": "a1b2c3",
        },
        {
            "callsign": "FLT2",
            "origin_country": "UK",
            "velocity": 280,
            "baro_altitude": 9000,
            "on_ground": True,
            "longitude": -0.45,
            "latitude": 51.47,
            "icao24": "d4e5f6",
        },
        {
            # Некорректные данные (должны быть пропущены)
            "callsign": "",
            "origin_country": "Germany",
            "velocity": 260,
            "baro_altitude": 11000,
        },
    ]

    result = Aeroplane.cast_to_object_list(data)

    assert len(result) == 2, "Должно быть 2 корректных объекта"
    assert result[0].callsign == "FLT1"
    assert result[1].callsign == "FLT2"
    assert result[1].on_ground == True


def test_str_representation():
    """Тест строкового представления"""

    # Самолет в воздухе
    a1 = create_test_aeroplane(
        callsign="AERO1", origin_country="France", velocity=250, baro_altitude=10000, on_ground=False
    )

    str_repr = a1.str()
    assert "AERO1" in str_repr
    assert "France" in str_repr
    assert "250" in str_repr
    assert "10000" in str_repr
    assert "В воздухе" in str_repr
    assert "На земле" not in str_repr

    # Самолет на земле
    a2 = create_test_aeroplane(
        callsign="AERO2", origin_country="Germany", velocity=None, baro_altitude=None, on_ground=True
    )

    str_repr = a2.str()
    assert "AERO2" in str_repr
    assert "Germany" in str_repr
    assert "N/A" in str_repr or "N/A" in str_repr
    assert "На земле" in str_repr
