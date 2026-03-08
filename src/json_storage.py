import json
import os
from typing import Any, Dict, List

from src.aeroplane import Aeroplane
from src.base_storage import BaseStorage


class JSONStorage(BaseStorage):
    """
    Класс для сохранения информации о самолетах в JSON-файл
    """

    def __init__(self, file_path: str = "data/aeroplanes.json"):
        """
        Инициализация JSON хранилища

        Args:
            file_path: Путь к JSON файлу
        """
        self._file_path = file_path
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Создание директории для файла, если она не существует"""
        directory = os.path.dirname(self._file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

    def _read_file(self) -> List[Dict[str, Any]]:
        """Чтение данных из JSON файла"""
        if not os.path.exists(self._file_path):
            return []

        try:
            with open(self._file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return []

    def _write_file(self, data: List[Dict[str, Any]]) -> bool:
        """Запись данных в JSON файл"""
        try:
            with open(self._file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка при записи в файл: {e}")
            return False

    def add_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """
        Добавление информации о самолете в JSON файл

        Args:
            aeroplane: Объект самолета

        Returns:
            True в случае успеха, False в случае ошибки
        """
        data = self._read_file()

        # Проверка на дубликаты (по callsign и icao24)
        for item in data:
            if item.get("callsign") == aeroplane.callsign and item.get("icao24") == aeroplane.icao24:
                print(f"Самолет {aeroplane.callsign} уже существует в хранилище")
                return False

        data.append(aeroplane.to_dict())
        return self._write_file(data)

    def add_aeroplanes(self, aeroplanes: List[Aeroplane]) -> bool:
        """
        Добавление нескольких самолетов в JSON файл

        Args:
            aeroplanes: Список объектов самолетов

        Returns:
            True в случае успеха, False в случае ошибки
        """
        data = self._read_file()
        existing_keys = {(item.get("callsign"), item.get("icao24")) for item in data}

        added_count = 0
        for aeroplane in aeroplanes:
            key = (aeroplane.callsign, aeroplane.icao24)
            if key not in existing_keys:
                data.append(aeroplane.to_dict())
                existing_keys.add(key)
                added_count += 1

        if added_count > 0:
            print(f"Добавлено {added_count} новых самолетов")
            return self._write_file(data)

        print("Новых самолетов для добавления не найдено")
        return True

    def get_aeroplanes(self, **criteria) -> List[Aeroplane]:
        """
        Получение данных из JSON файла по указанным критериям

        Args:
            **criteria: Критерии фильтрации
                - origin_country: фильтр по стране регистрации
                - min_altitude: минимальная высота
                - max_altitude: максимальная высота
                - on_ground: на земле/в воздухе
                - callsign: фильтр по позывному
        Returns:
                    Список объектов самолетов
        """
        data = self._read_file()
        aeroplanes = Aeroplane.cast_to_object_list(data)

        # Применение фильтров
        if "origin_country" in criteria and criteria["origin_country"]:
            country = criteria["origin_country"].lower()
            aeroplanes = [a for a in aeroplanes if a.origin_country and country in a.origin_country.lower()]

        if "min_altitude" in criteria and criteria["min_altitude"] is not None:
            min_alt = float(criteria["min_altitude"])
            aeroplanes = [a for a in aeroplanes if a.baro_altitude is not None and a.baro_altitude >= min_alt]

        if "max_altitude" in criteria and criteria["max_altitude"] is not None:
            max_alt = float(criteria["max_altitude"])
            aeroplanes = [a for a in aeroplanes if a.baro_altitude is not None and a.baro_altitude <= max_alt]

        if "on_ground" in criteria and criteria["on_ground"] is not None:
            on_ground = bool(criteria["on_ground"])
            aeroplanes = [a for a in aeroplanes if a.on_ground == on_ground]

        if "callsign" in criteria and criteria["callsign"]:
            callsign = criteria["callsign"].lower()
            aeroplanes = [a for a in aeroplanes if callsign in a.callsign.lower()]

        return aeroplanes

    def delete_aeroplane(self, aeroplane: Aeroplane) -> bool:
        """
        Удаление информации о самолете из JSON файла

        Args:
            aeroplane: Объект самолета

        Returns:
            True в случае успеха, False в случае ошибки
        """
        data = self._read_file()
        initial_length = len(data)

        # Удаление по совпадению callsign и icao24
        data = [
            item
            for item in data
            if not (item.get("callsign") == aeroplane.callsign and item.get("icao24") == aeroplane.icao24)
        ]

        if len(data) < initial_length:
            return self._write_file(data)

        print(f"Самолет {aeroplane.callsign} не найден в хранилище")
        return False

    def delete_aeroplanes(self, **criteria) -> int:
        """
        Удаление самолетов по критериям

        Args:
            **criteria: Критерии для удаления

        Returns:
            Количество удаленных самолетов
        """
        data = self._read_file()
        initial_length = len(data)

        # Применение критериев удаления
        if "origin_country" in criteria and criteria["origin_country"]:
            country = criteria["origin_country"].lower()
            data = [
                item
                for item in data
                if not (item.get("origin_country") and country in item.get("origin_country", "").lower())
            ]

        if "on_ground" in criteria and criteria["on_ground"] is not None:
            on_ground = bool(criteria["on_ground"])
            data = [item for item in data if item.get("on_ground") != on_ground]

        deleted_count = initial_length - len(data)

        if deleted_count > 0:
            self._write_file(data)
            print(f"Удалено {deleted_count} самолетов")
        else:
            print("Самолеты для удаления не найдены")

        return deleted_count

    def clear(self) -> bool:
        """
        Очистка JSON файла

        Returns:
            True в случае успеха, False в случае ошибки
        """
        return self._write_file([])
