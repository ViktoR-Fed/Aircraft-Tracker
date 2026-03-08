import json
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional

from src.aeroplane import Aeroplane
from src.json_storage import JSONStorage


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
    """
    Создание тестового самолета с учетом конструктора Aeroplane

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


def create_temp_storage():
    """Создание временного хранилища для тестов"""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "test_aeroplanes.json")
    storage = JSONStorage(file_path)
    return storage, temp_dir, file_path


def cleanup_temp_dir(temp_dir: str):
    """Очистка временной директории"""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


# Тесты для JSONStorage
def test_init_and_directory_creation():
    """Тест инициализации и создания директории"""

    with tempfile.TemporaryDirectory() as temp_dir:
        nested_path = os.path.join(temp_dir, "nested", "folder", "test.json")
        storage = JSONStorage(nested_path)

        assert os.path.exists(os.path.dirname(nested_path)), "Директория не создана"
        assert storage._file_path == nested_path, "Неправильный путь к файлу"


def test_add_aeroplane():
    """Тест добавления одного самолета"""

    storage, temp_dir, file_path = create_temp_storage()

    try:
        # Создаем самолет с учетом конструктора Aeroplane
        aeroplane = create_test_aeroplane(
            callsign="TEST123",
            icao24="abc123",
            origin_country="Russia",
            velocity=250.0,
            baro_altitude=10000.0,
            on_ground=False,
            longitude=37.62,
            latitude=55.75,
        )

        # Добавляем самолет
        result = storage.add_aeroplane(aeroplane)
        assert result == True, "Добавление должно быть успешным"

        # Проверяем, что файл создан
        assert os.path.exists(file_path), "Файл не создан"

        # Проверяем содержимое файла
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1, "Должен быть 1 самолет"
        assert data[0]["callsign"] == "TEST123", "Неправильный callsign"
        assert data[0]["icao24"] == "abc123", "Неправильный icao24"
        assert data[0]["origin_country"] == "Russia", "Неправильная страна"
        assert data[0]["velocity"] == 250.0, "Неправильная скорость"
        assert data[0]["baro_altitude"] == 10000.0, "Неправильная высота"
        assert data[0]["on_ground"] == False, "Неправильный on_ground"
        assert data[0]["longitude"] == 37.62, "Неправильная долгота"
        assert data[0]["latitude"] == 55.75, "Неправильная широта"

        # Проверка на дубликат (по callsign и icao24)
        result = storage.add_aeroplane(aeroplane)
        assert result == False, "Не должно добавлять дубликат"

        # Проверка, что дубликат не добавился
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1, "Дубликат не должен добавиться"

    finally:
        cleanup_temp_dir(temp_dir)


def test_add_aeroplanes():
    """Тест добавления нескольких самолетов"""

    storage, temp_dir, file_path = create_temp_storage()

    try:
        # Создаем тестовые самолеты с учетом конструктора Aeroplane
        aeroplane1 = create_test_aeroplane(
            callsign="TEST1", icao24="111111", origin_country="USA", velocity=300.0, baro_altitude=12000.0
        )
        aeroplane2 = create_test_aeroplane(
            callsign="TEST2", icao24="222222", origin_country="UK", velocity=280.0, baro_altitude=9000.0
        )
        aeroplane3 = create_test_aeroplane(
            callsign="TEST3", icao24="333333", origin_country="Germany", velocity=260.0, baro_altitude=11000.0
        )

        # Добавляем список
        result = storage.add_aeroplanes([aeroplane1, aeroplane2])
        assert result == True, "Добавление должно быть успешным"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2, "Должно быть 2 самолета"

        # Добавляем с дубликатом и новым
        result = storage.add_aeroplanes([aeroplane1, aeroplane3])
        assert result == True, "Добавление должно быть успешным"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 3, "Должно быть 3 самолета (дубликат не добавился)"

        callsigns = [item["callsign"] for item in data]
        assert "TEST1" in callsigns
        assert "TEST2" in callsigns
        assert "TEST3" in callsigns

    finally:
        cleanup_temp_dir(temp_dir)


def test_get_aeroplanes():
    """Тест получения самолетов с фильтрацией"""

    storage, temp_dir, _ = create_temp_storage()

    try:

        aeroplanes = [
            create_test_aeroplane(
                callsign="RUS1",
                icao24="111111",
                origin_country="Russia",
                baro_altitude=10000.0,
                on_ground=False,
                velocity=250.0,
                longitude=37.62,
                latitude=55.75,
            ),
            create_test_aeroplane(
                callsign="RUS2",
                icao24="222222",
                origin_country="Russia",
                baro_altitude=5000.0,
                on_ground=False,
                velocity=200.0,
                longitude=30.0,
                latitude=60.0,
            ),
            create_test_aeroplane(
                callsign="USA1",
                icao24="333333",
                origin_country="United States",
                baro_altitude=20000.0,
                on_ground=False,
                velocity=300.0,
                longitude=-73.98,
                latitude=40.75,
            ),
            create_test_aeroplane(
                callsign="GER1",
                icao24="444444",
                origin_country="Germany",
                baro_altitude=0.0,
                on_ground=True,
                velocity=0.0,
                longitude=13.40,
                latitude=52.52,
            ),
        ]

        storage.add_aeroplanes(aeroplanes)

        # Тест фильтра по стране
        result = storage.get_aeroplanes(origin_country="Russia")
        assert len(result) == 2, "Должно быть 2 российских самолета"
        assert all(a.origin_country == "Russia" for a in result)

        # Тест фильтра по минимальной высоте
        result = storage.get_aeroplanes(min_altitude=8000.0)
        assert len(result) == 2, "Должно быть 2 самолета выше 8000"
        assert all(a.baro_altitude >= 8000.0 for a in result if a.baro_altitude is not None)

        # Тест фильтра по максимальной высоте
        result = storage.get_aeroplanes(max_altitude=15000.0)
        assert len(result) == 3, "Должно быть 3 самолета ниже 15000"

        # Тест фильтра по on_ground
        result = storage.get_aeroplanes(on_ground=True)
        assert len(result) == 1, "Должен быть 1 самолет на земле"
        assert result[0].callsign == "GER1"
        assert result[0].on_ground == True

        # Тест фильтра по callsign
        result = storage.get_aeroplanes(callsign="RUS")
        assert len(result) == 2, "Должно быть 2 самолета с RUS в callsign"

        # Тест комбинированного фильтра
        result = storage.get_aeroplanes(origin_country="Russia", min_altitude=8000.0)
        assert len(result) == 1, "Должен быть 1 российский самолет выше 8000"
        assert result[0].callsign == "RUS1"

    finally:
        cleanup_temp_dir(temp_dir)


def test_delete_aeroplane():
    """Тест удаления одного самолета"""

    storage, temp_dir, _ = create_temp_storage()

    try:
        # Добавляем тестовые данные
        aeroplane1 = create_test_aeroplane(callsign="TEST1", icao24="111111")
        aeroplane2 = create_test_aeroplane(callsign="TEST2", icao24="222222")

        storage.add_aeroplanes([aeroplane1, aeroplane2])

        # Удаляем первый самолет
        result = storage.delete_aeroplane(aeroplane1)
        assert result == True, "Удаление должно быть успешным"

        # Проверяем, что остался только второй
        result = storage.get_aeroplanes()
        assert len(result) == 1, "Должен остаться 1 самолет"
        assert result[0].callsign == "TEST2"

        # Пытаемся удалить несуществующий
        aeroplane3 = create_test_aeroplane(callsign="TEST3", icao24="333333")
        result = storage.delete_aeroplane(aeroplane3)
        assert result == False, "Удаление несуществующего должно вернуть False"

    finally:
        cleanup_temp_dir(temp_dir)


def test_delete_aeroplanes():
    """Тест удаления нескольких самолетов по критериям"""

    storage, temp_dir, _ = create_temp_storage()

    try:
        # Добавляем тестовые данные
        aeroplanes = [
            create_test_aeroplane(callsign="RUS1", icao24="111111", origin_country="Russia", on_ground=False),
            create_test_aeroplane(callsign="RUS2", icao24="222222", origin_country="Russia", on_ground=True),
            create_test_aeroplane(callsign="USA1", icao24="333333", origin_country="United States", on_ground=False),
        ]

        storage.add_aeroplanes(aeroplanes)

        # Удаляем российские самолеты
        deleted_count = storage.delete_aeroplanes(origin_country="Russia")
        assert deleted_count == 2, "Должно быть удалено 2 самолета"

        result = storage.get_aeroplanes()
        assert len(result) == 1, "Должен остаться 1 самолет"
        assert result[0].callsign == "USA1"

        # Удаляем самолеты на земле (их нет после предыдущего удаления)
        deleted_count = storage.delete_aeroplanes(on_ground=True)
        assert deleted_count == 0, "Не должно быть удаленных самолетов"

        # Добавляем еще и удаляем по комбинированному критерию
        storage.add_aeroplanes(aeroplanes)

        deleted_count = storage.delete_aeroplanes(origin_country="Russia", on_ground=True)
        assert deleted_count == 2, "Должен быть удален 1 самолет (RUS2)"

    finally:
        cleanup_temp_dir(temp_dir)


def test_clear():
    """Тест очистки хранилища"""

    storage, temp_dir, _ = create_temp_storage()

    try:
        # Добавляем данные
        aeroplane = create_test_aeroplane()
        storage.add_aeroplane(aeroplane)

        # Проверяем, что данные есть
        result = storage.get_aeroplanes()
        assert len(result) == 1

        # Очищаем
        result = storage.clear()
        assert result == True, "Очистка должна быть успешной"

        # Проверяем, что данных нет
        result = storage.get_aeroplanes()
        assert len(result) == 0, "После очистки не должно быть данных"

    finally:
        cleanup_temp_dir(temp_dir)


def test_error_handling():
    """Тест обработки ошибок"""

    # Тест с несуществующей директорией
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_path = os.path.join(temp_dir, "nonexistent", "subfolder", "test.json")
        storage = JSONStorage(invalid_path)

        # Чтение из несуществующего файла
        result = storage.get_aeroplanes()
        assert len(result) == 0, "Должен вернуть пустой список"

        # Запись должна создать директорию
        aeroplane = create_test_aeroplane()
        result = storage.add_aeroplane(aeroplane)
        assert result == True, "Запись должна создать директорию и файл"
        assert os.path.exists(invalid_path), "Файл должен быть создан"

    # Тест с поврежденным JSON файлом
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "corrupt.json")

        # Создаем поврежденный JSON файл
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("{this is not valid json")

        storage = JSONStorage(file_path)

        # Чтение поврежденного файла должно вернуть пустой список
        result = storage.get_aeroplanes()
        assert len(result) == 0, "Поврежденный JSON должен давать пустой список"

        # Запись должна перезаписать файл
        aeroplane = create_test_aeroplane()
        result = storage.add_aeroplane(aeroplane)
        assert result == True, "Запись должна быть успешной"

        # Проверяем, что файл теперь корректный
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["callsign"] == "TEST123"


def test_data_integrity():
    """Тест целостности данных (соответствие классу Aeroplane)"""

    storage, temp_dir, _ = create_temp_storage()

    try:
        # Создаем самолет со всеми полями, которые есть в Aeroplane
        original = create_test_aeroplane(
            callsign="INTEGRITY1",
            icao24="999999",
            origin_country="Testland",
            velocity=300.5,
            baro_altitude=15000.0,
            on_ground=False,
            longitude=20.5,
            latitude=10.5,
        )

        # Сохраняем
        storage.add_aeroplane(original)

        # Читаем обратно
        result = storage.get_aeroplanes()
        assert len(result) == 1
        loaded = result[0]

        # Проверяем все поля, которые есть в Aeroplane
        assert loaded.callsign == original.callsign
        assert loaded.icao24 == original.icao24
        assert loaded.origin_country == original.origin_country
        assert loaded.velocity == original.velocity
        assert loaded.baro_altitude == original.baro_altitude
        assert loaded.on_ground == original.on_ground
        assert loaded.longitude == original.longitude
        assert loaded.latitude == original.latitude

        # Проверяем, что нет лишних полей
        assert not hasattr(loaded, "true_track")
        assert not hasattr(loaded, "vertical_rate")
        assert not hasattr(loaded, "sensors")
        assert not hasattr(loaded, "geo_altitude")
        assert not hasattr(loaded, "squawk")
        assert not hasattr(loaded, "spi")
        assert not hasattr(loaded, "position_source")

    finally:
        cleanup_temp_dir(temp_dir)
