from typing import Any, Union


# Функции валидации
def validate_string(value: Any) -> bool:
    """Проверка, что значение является непустой строкой"""
    return isinstance(value, str) and value.strip() != ""


def validate_number(value: Union[int, float], field_name: str) -> float:
    """Проверка, что значение является числом"""
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} должен быть числом")
    return float(value)


def validate_positive_number(value: Union[int, float], field_name: str) -> float:
    """Проверка, что значение является положительным числом"""
    num = validate_number(value, field_name)
    if num < 0:
        raise ValueError(f"{field_name} должен быть неотрицательным")
    return num


def validate_boolean(value: Any) -> bool:
    """Проверка, что значение является булевым"""
    return bool(value)


def validate_longitude(value: float) -> float:
    """Проверка корректности долготы"""
    if not -180 <= value <= 180:
        raise ValueError(f"Долгота должна быть в диапазоне [-180, 180], получено {value}")
    return value


def validate_latitude(value: float) -> float:
    """Проверка корректности широты"""
    if not -90 <= value <= 90:
        raise ValueError(f"Широта должна быть в диапазоне [-90, 90], получено {value}")
    return value


def test_validate_string():
    print("\n=== Тестирование validate_string ===")

    # Позитивные тесты
    assert validate_string("hello") == True, "Должно быть True для непустой строки"
    assert validate_string("  hello  ") == True, "Должно быть True для строки с пробелами"

    # Негативные тесты
    assert validate_string("") == False, "Должно быть False для пустой строки"
    assert validate_string("   ") == False, "Должно быть False для строки из пробелов"
    assert validate_string(123) == False, "Должно быть False для числа"
    assert validate_string(None) == False, "Должно быть False для None"
    assert validate_string([]) == False, "Должно быть False для списка"


def test_validate_number():
    print("\n=== Тестирование validate_number ===")

    # Позитивные тесты
    assert validate_number(10, "возраст") == 10.0, "Должно вернуть float для int"
    assert validate_number(10.5, "возраст") == 10.5, "Должно вернуть float для float"
    assert validate_number(0, "возраст") == 0.0, "Должно работать с нулем"
    assert validate_number(-5, "возраст") == -5.0, "Должно работать с отрицательными"

    # Негативные тесты
    try:
        validate_number("10", "возраст")
        assert False, "Должно быть исключение для строки"
    except ValueError as e:
        assert str(e) == "возраст должен быть числом", f"Неправильное сообщение: {e}"

    try:
        validate_number(None, "возраст")
        assert False, "Должно быть исключение для None"
    except ValueError as e:
        assert "возраст должен быть числом" in str(e), f"Неправильное сообщение: {e}"


def test_validate_positive_number():
    print("\n=== Тестирование validate_positive_number ===")

    # Позитивные тесты
    assert validate_positive_number(10, "возраст") == 10.0, "Положительное число"
    assert validate_positive_number(0, "возраст") == 0.0, "Ноль должен проходить"
    assert validate_positive_number(10.5, "возраст") == 10.5, "Положительное float"

    # Негативные тесты
    try:
        validate_positive_number(-5, "возраст")
        assert False, "Должно быть исключение для отрицательного"
    except ValueError as e:
        assert str(e) == "возраст должен быть неотрицательным", f"Неправильное сообщение: {e}"

    try:
        validate_positive_number("10", "возраст")
        assert False, "Должно быть исключение для строки"
    except ValueError as e:
        assert "возраст должен быть числом" in str(e), f"Неправильное сообщение: {e}"


def test_validate_boolean():
    print("\n=== Тестирование validate_boolean ===")

    # Тесты
    assert validate_boolean(True) == True, "True должно быть True"
    assert validate_boolean(False) == False, "False должно быть False"
    assert validate_boolean(1) == True, "1 должно преобразовываться в True"
    assert validate_boolean(0) == False, "0 должно преобразовываться в False"
    assert validate_boolean("") == False, "Пустая строка -> False"
    assert validate_boolean("text") == True, "Непустая строка -> True"
    assert validate_boolean([]) == False, "Пустой список -> False"
    assert validate_boolean([1, 2]) == True, "Непустой список -> True"
    assert validate_boolean(None) == False, "None -> False"


def test_validate_coordinates():
    print("\n=== Тестирование координат ===")

    # Тесты долготы
    assert validate_longitude(0) == 0, "Нулевая долгота"
    assert validate_longitude(180) == 180, "Максимальная долгота"
    assert validate_longitude(-180) == -180, "Минимальная долгота"

    try:
        validate_longitude(181)
        assert False, "Должно быть исключение для >180"
    except ValueError as e:
        assert "Долгота должна быть в диапазоне" in str(e)

    try:
        validate_longitude(-181)
        assert False, "Должно быть исключение для <-180"
    except ValueError as e:
        assert "Долгота должна быть в диапазоне" in str(e)

    # Тесты широты
    assert validate_latitude(0) == 0, "Нулевая широта"
    assert validate_latitude(90) == 90, "Максимальная широта"
    assert validate_latitude(-90) == -90, "Минимальная широта"

    try:
        validate_latitude(91)
        assert False, "Должно быть исключение для >90"
    except ValueError as e:
        assert "Широта должна быть в диапазоне" in str(e)

    try:
        validate_latitude(-91)
        assert False, "Должно быть исключение для <-91"
    except ValueError as e:
        assert "Широта должна быть в диапазоне" in str(e)
