import os
import sys
from typing import List, Optional

from src.aeroplane import Aeroplane
from src.aeroplane_api import AeroplaneAPI
from src.json_storage import JSONStorage

# Добавление пути для импорта модулей src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def print_aeroplanes(aeroplanes: List[Aeroplane], title: str = "Самолеты") -> None:
    """
    Вывод информации о самолетах в консоль

    Args:
        aeroplanes: Список самолетов
        title: Заголовок вывода
    """
    if not aeroplanes:
        print(f"\n{title}: Не найдено")
        return

    print(f"\n{title} (найдено: {len(aeroplanes)}):")
    for i, aeroplane in enumerate(aeroplanes, 1):
        print(f"{i}. {aeroplane}")


def sort_aeroplanes_by_altitude(aeroplanes: List[Aeroplane], reverse: bool = True) -> List[Aeroplane]:
    """
    Сортировка самолетов по высоте

    Args:
        aeroplanes: Список самолетов
        reverse: Сортировка по убыванию (True) или возрастанию (False)

    Returns:
        Отсортированный список
    """
    # Фильтруем самолеты без данных о высоте
    valid_aeroplanes = [a for a in aeroplanes if a.baro_altitude is not None]
    invalid_aeroplanes = [a for a in aeroplanes if a.baro_altitude is None]

    # Сортируем валидные самолеты
    sorted_valid = sorted(valid_aeroplanes, reverse=reverse)

    # Возвращаем отсортированные + невалидные в конце
    return sorted_valid + invalid_aeroplanes


def get_top_n_aeroplanes(aeroplanes: List[Aeroplane], n: int) -> List[Aeroplane]:
    """
    Получение топ N самолетов по высоте

    Args:
        aeroplanes: Список самолетов
        n: Количество самолетов для вывода

    Returns:
        Список топ N самолетов
    """
    sorted_aeroplanes = sort_aeroplanes_by_altitude(aeroplanes, reverse=True)
    return sorted_aeroplanes[:n]


def filter_by_origin_country(aeroplanes: List[Aeroplane], countries: List[str]) -> List[Aeroplane]:
    """
    Фильтрация самолетов по стране регистрации

    Args:
        aeroplanes: Список самолетов
        countries: Список стран для фильтрации

    Returns:
        Отфильтрованный список
    """
    if not countries:
        return aeroplanes

    countries_lower = [c.lower() for c in countries]
    filtered = []

    for aeroplane in aeroplanes:
        if aeroplane.origin_country:
            country_lower = aeroplane.origin_country.lower()
            if any(country in country_lower for country in countries_lower):
                filtered.append(aeroplane)

    return filtered


def filter_by_altitude_range(
    aeroplanes: List[Aeroplane], min_alt: Optional[float], max_alt: Optional[float]
) -> List[Aeroplane]:
    """
    Фильтрация самолетов по диапазону высот

    Args:
        aeroplanes: Список самолетов
        min_alt: Минимальная высота
        max_alt: Максимальная высота

    Returns:
        Отфильтрованный список
    """
    if min_alt is None and max_alt is None:
        return aeroplanes

    filtered = []

    for aeroplane in aeroplanes:
        if aeroplane.baro_altitude is None:
            continue

        if min_alt is not None and aeroplane.baro_altitude < min_alt:
            continue

        if max_alt is not None and aeroplane.baro_altitude > max_alt:
            continue

        filtered.append(aeroplane)

    return filtered


def filter_by_velocity_range(
    aeroplanes: List[Aeroplane], min_vel: Optional[float], max_vel: Optional[float]
) -> List[Aeroplane]:
    """
    Фильтрация самолетов по диапазону скорости

    Args:
        aeroplanes: Список самолетов
    min_vel: Минимальная скорость
            max_vel: Максимальная скорость

        Returns:
            Отфильтрованный список
    """
    if min_vel is None and max_vel is None:
        return aeroplanes

    filtered = []

    for aeroplane in aeroplanes:
        if aeroplane.velocity is None:
            continue

        if min_vel is not None and aeroplane.velocity < min_vel:
            continue

        if max_vel is not None and aeroplane.velocity > max_vel:
            continue

        filtered.append(aeroplane)

    return filtered


def parse_range_input(range_str: str) -> tuple:
    """
    Парсинг строки диапазона

    Args:
        range_str: Строка вида "min - max" или "min" или "max"

    Returns:
        Кортеж (min, max)
    """
    if not range_str or range_str.strip() == "":
        return None, None

    parts = range_str.split("-")

    if len(parts) == 1:
        # Только одно значение
        try:
            value = float(parts[0].strip())
            return value, value
        except ValueError:
            return None, None

    elif len(parts) == 2:
        # Диапазон
        try:
            min_val = float(parts[0].strip()) if parts[0].strip() else None
            max_val = float(parts[1].strip()) if parts[1].strip() else None
            return min_val, max_val
        except ValueError:
            return None, None

    return None, None


def user_interaction() -> None:
    """Функция для взаимодействия с пользователем через консоль"""

    print("Программа для отслеживания самолетов в воздушном пространстве")

    # Инициализация компонентов
    api = AeroplaneAPI()
    storage = JSONStorage()

    while True:
        print("\nМеню:")
        print("1.Получить информацию о самолетах в стране")
        print("2.Показать топ N самолетов по высоте")
        print("3.Фильтр по стране регистрации")
        print("4.Фильтр по диапазону высот")
        print("5.Фильтр по диапазону скорости")
        print("6.Сохранить текущие данные в файл")
        print("7.Загрузить данные из файла")
        print("8.Показать статистику")
        print("9.Сравнить два самолета")
        print("0.Выход")

        choice = input("\nВыберите действие (0-9): ").strip()

        if choice == "1":
            # Получение информации о самолетах в стране
            country = input("Введите название страны (например, Russia, Spain, Canada): ").strip()
            if not country:
                print("Название страны не может быть пустым")
                continue

            print(f"\nЗапрос информации о самолетах в {country}...")
            aeroplanes_data = api.get_aeroplanes(country)

            if aeroplanes_data:
                aeroplanes = Aeroplane.cast_to_object_list(aeroplanes_data)
                print_aeroplanes(aeroplanes, f"Самолеты в {country}")

                # Сохраняем в атрибут для дальнейшего использования
                user_interaction.current_aeroplanes = aeroplanes
            else:
                print(f"Не удалось получить данные о самолетах для страны {country}")
                user_interaction.current_aeroplanes = []

        elif choice == "2":
            # Топ N самолетов по высоте
            if not hasattr(user_interaction, "current_aeroplanes") or not user_interaction.current_aeroplanes:
                print("Сначала получите данные о самолетах (пункт 1)")
                continue

            try:
                n = int(input("Введите количество самолетов для вывода в топ: ").strip())
                if n <= 0:
                    print("Количество должно быть положительным числом")
                continue
            except ValueError:
                print("Некорректный ввод. Введите целое положительное число")
                continue
            top_aeroplanes = get_top_n_aeroplanes(user_interaction.current_aeroplanes, n)
            print_aeroplanes(top_aeroplanes, f"Топ {n} самолетов по высоте")

        elif choice == "3":
            # Фильтр по стране регистрации
            if not hasattr(user_interaction, "current_aeroplanes") or not user_interaction.current_aeroplanes:
                print("Сначала получите данные о самолетах (пункт 1)")
                continue

            countries_input = input("Введите названия стран для фильтрации (через пробел): ").strip()
            if not countries_input:
                print("Не указаны страны для фильтрации")
                continue

            countries = countries_input.split()
            filtered = filter_by_origin_country(user_interaction.current_aeroplanes, countries)
            print_aeroplanes(filtered, f"Самолеты из стран: {', '.join(countries)}")

        elif choice == "4":
            # Фильтр по диапазону высот
            if not hasattr(user_interaction, "current_aeroplanes") or not user_interaction.current_aeroplanes:
                print("Сначала получите данные о самолетах (пункт 1)")
                continue

            range_str = input("Введите диапазон высот (пример: 10000 - 15000 или 10000): ").strip()
            min_alt, max_alt = parse_range_input(range_str)

            filtered = filter_by_altitude_range(user_interaction.current_aeroplanes, min_alt, max_alt)

            range_desc = ""
            if min_alt is not None and max_alt is not None:
                if min_alt == max_alt:
                    range_desc = f"на высоте {min_alt} м"
                else:
                    range_desc = f"в диапазоне высот {min_alt} - {max_alt} м"
            elif min_alt is not None:
                range_desc = f"на высоте не менее {min_alt} м"
            elif max_alt is not None:
                range_desc = f"на высоте не более {max_alt} м"
            else:
                range_desc = "все самолеты"

            print_aeroplanes(filtered, f"Самолеты {range_desc}")

        elif choice == "5":
            # Фильтр по диапазону скорости
            if not hasattr(user_interaction, "current_aeroplanes") or not user_interaction.current_aeroplanes:
                print("Сначала получите данные о самолетах (пункт 1)")
                continue

            range_str = input("Введите диапазон скорости (пример: 200 - 300): ").strip()
            min_vel, max_vel = parse_range_input(range_str)

            filtered = filter_by_velocity_range(user_interaction.current_aeroplanes, min_vel, max_vel)

            range_desc = ""
            if min_vel is not None and max_vel is not None:
                if min_vel == max_vel:
                    range_desc = f"со скоростью {min_vel} м/с"
                else:
                    range_desc = f"со скоростью {min_vel} - {max_vel} м/с"
            elif min_vel is not None:
                range_desc = f"со скоростью не менее {min_vel} м/с"
            elif max_vel is not None:
                range_desc = f"со скоростью не более {max_vel} м/с"
            else:
                range_desc = "все самолеты"

            print_aeroplanes(filtered, f"Самолеты {range_desc}")

        elif choice == "6":
            # Сохранение в файл
            if not hasattr(user_interaction, "current_aeroplanes") or not user_interaction.current_aeroplanes:
                print("Нет данных для сохранения")
                continue
            success = storage.add_aeroplanes(user_interaction.current_aeroplanes)
            if success:
                print("Данные успешно сохранены в файл")
            else:
                print("Ошибка при сохранении данных")

        elif choice == "7":
            # Загрузка из файла
            aeroplanes = storage.get_aeroplanes()
            if aeroplanes:
                user_interaction.current_aeroplanes = aeroplanes
                print_aeroplanes(aeroplanes, "Загруженные данные")
            else:
                print("Файл пуст или не найден")

        elif choice == "8":
            # Показать статистику
            if not hasattr(user_interaction, "current_aeroplanes") or not user_interaction.current_aeroplanes:
                print("Нет данных для анализа")
                continue

            aeroplanes = user_interaction.current_aeroplanes

            # Общая статистика
            total = len(aeroplanes)
            on_ground = sum(1 for a in aeroplanes if a.on_ground)
            in_air = total - on_ground

            # Статистика по высоте
            altitudes = [a.baro_altitude for a in aeroplanes if a.baro_altitude is not None]
            if altitudes:
                max_alt = max(altitudes)
                min_alt = min(altitudes)
                avg_alt = sum(altitudes) / len(altitudes)
            else:
                max_alt = min_alt = avg_alt = None

            # Статистика по скорости
            velocities = [a.velocity for a in aeroplanes if a.velocity is not None]
            if velocities:
                max_vel = max(velocities)
                min_vel = min(velocities)
                avg_vel = sum(velocities) / len(velocities)
            else:
                max_vel = min_vel = avg_vel = None

            # Статистика по странам
            countries = {}
            for a in aeroplanes:
                if a.origin_country:
                    countries[a.origin_country] = countries.get(a.origin_country, 0) + 1

            print(f"Всего самолетов: {total}")
            print(f"В воздухе: {in_air}")
            print(f"На земле: {on_ground}")

            if altitudes:
                print("\nВысота (м):")
                print(f"Максимальная: {max_alt:.1f}")
                print(f"Минимальная: {min_alt:.1f}")
                print(f"Средняя: {avg_alt:.1f}")

            if velocities:
                print("\nСкорость (м/с):")
                print(f"Максимальная: {max_vel:.1f}")
                print(f"Минимальная: {min_vel:.1f}")
                print(f"Средняя: {avg_vel:.1f}")

            if countries:
                print("\nТоп-5 стран регистрации:")
                sorted_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]
                for country, count in sorted_countries:
                    print(f"{country}: {count}")

        elif choice == "9":
            # Сравнение двух самолетов
            if not hasattr(user_interaction, "current_aeroplanes") or len(user_interaction.current_aeroplanes) < 2:
                print("Недостаточно данных для сравнения (нужно минимум 2 самолета)")
                continue

            aeroplanes = user_interaction.current_aeroplanes

            print("\nДоступные самолеты:")
            for i, a in enumerate(aeroplanes[:10], 1):  # Показываем первые 10
                print(f"{i}. {a.callsign} ({a.origin_country})")

            try:
                idx1 = int(input("Введите номер первого самолета: ")) - 1
                idx2 = int(input("Введите номер второго самолета: ")) - 1

                if idx1 < 0 or idx1 >= len(aeroplanes) or idx2 < 0 or idx2 >= len(aeroplanes):
                    print("Некорректные номера")
                    continue

                a1 = aeroplanes[idx1]
                a2 = aeroplanes[idx2]

                print(f"Самолет 1: {a1}")
                print(f"Самолет 2: {a2}")

                # Сравнение по высоте
                if a1 > a2:
                    print(f"\nСамолет 1 ({a1.callsign}) летит выше самолета 2 ({a2.callsign})")
                elif a1 < a2:
                    print(f"\nСамолет 2 ({a2.callsign}) летит выше самолета 1 ({a1.callsign})")
                elif a1.baro_altitude is not None and a2.baro_altitude is not None:
                    print("\nСамолеты летят на одинаковой высоте")

                # Сравнение по скорости
                if a1.faster_than(a2):
                    print(f"Самолет 1 ({a1.callsign}) быстрее самолета 2 ({a2.callsign})")
                elif a2.faster_than(a1):
                    print(f"Самолет 2 ({a2.callsign}) быстрее самолета 1 ({a1.callsign})")
                elif a1.velocity is not None and a2.velocity is not None:
                    print("Самолеты летят с одинаковой скоростью")

            except ValueError:
                print("Некорректный ввод")

        elif choice == "0":
            print("Программа завершена. До свидания!")
            break

        else:
            print("Некорректный выбор. Пожалуйста, выберите действие от 0 до 9")


if __name__ == "__main__":
    # Инициализация атрибута для хранения текущих самолетов
    user_interaction()
    user_interaction.current_aeroplanes = []
