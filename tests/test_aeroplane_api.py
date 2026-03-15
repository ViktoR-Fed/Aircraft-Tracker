
from unittest.mock import  Mock, patch


import requests

from src.aeroplane_api import AeroplaneAPI


# Фикстуры и вспомогательные функции
def create_mock_response(status_code=200, json_data=None):
    """Создание мок-ответа для requests"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_data or {}
    return mock_response


def create_mock_nominatim_response(country_name="Russia"):
    """Создание мок-ответа от Nominatim API"""
    return [
        {
            "place_id": 12345,
            "licence": "Test Licence",
            "osm_type": "relation",
            "osm_id": 123456,
            "boundingbox": ["40.0", "80.0", "20.0", "180.0"],  # [south, north, west, east]
            "lat": "55.75",
            "lon": "37.62",
            "display_name": f"{country_name}, Eurasia",
            "class": "place",
            "type": "country",
            "importance": 0.7,
        }
    ]


def create_mock_opensky_response():
    """Создание мок-ответа от OpenSky API"""
    return {
        "time": 1641234567,
        "states": [
            [
                "abc123",  # icao24
                "AFL101  ",  # callsign (с пробелами)
                "Russia",  # origin_country
                1641234567,  # time_position
                1641234567,  # last_contact
                37.62,  # longitude
                55.75,  # latitude
                10000.0,  # baro_altitude
                False,  # on_ground
                250.0,  # velocity
                90.0,  # true_track
                0.0,  # vertical_rate
                [1, 2, 3],  # sensors
                11000.0,  # geo_altitude
                "1234",  # squawk
                False,  # spi
                0,  # position_source
            ],
            [
                "def456",
                "DLH202",
                "Germany",
                1641234567,
                1641234567,
                13.40,
                52.52,
                12000.0,
                False,
                280.0,
                180.0,
                0.5,
                [4, 5, 6],
                13000.0,
                "5678",
                False,
                1,
            ],
        ],
    }


# Тесты для AeroplaneAPI
def test_init():
    """Тест инициализации класса"""

    api = AeroplaneAPI()

    assert api.nominatim_url == "https://nominatim.openstreetmap.org/search"
    assert api.opensky_url == "https://opensky-network.org/api/states/all"
    assert api.user_agent == "AeroplaneTracker/1.0"


@patch("requests.get")
def test_connect_success(mock_get):
    """Тест успешного подключения к API"""

    # Настройка мока
    mock_response = create_mock_response(200, {"test": "data"})
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api._connect("https://test.com/api", params={"key": "value"})

    # Проверки
    assert result == {"test": "data"}, "Должен вернуть JSON данные"
    mock_get.assert_called_once_with(
        "https://test.com/api", params={"key": "value"}, headers={"User-Agent": "AeroplaneTracker/1.0"}, timeout=10
    )


@patch("requests.get")
def test_connect_error_status(mock_get):
    """Тест подключения с ошибкой статуса"""

    # Настройка мока
    mock_response = create_mock_response(404, None)
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api._connect("https://test.com/api")

    assert result is None, "При ошибке статуса должен вернуть None"


@patch("requests.get")
def test_connect_exception(mock_get):
    """Тест подключения с исключением"""

    # Настройка мока на выброс исключения
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    api = AeroplaneAPI()
    result = api._connect("https://test.com/api")

    assert result is None, "При исключении должен вернуть None"


@patch("requests.get")
def test_get_country_coordinates_success(mock_get):
    """Тест успешного получения координат страны"""

    # Настройка мока
    mock_response = create_mock_response(200, create_mock_nominatim_response("Russia"))
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api.get_country_coordinates("Russia")

    # Проверки
    assert result is not None, "Должен вернуть координаты"
    assert len(result) == 4, "Должно быть 4 координаты"
    assert result[0] == "40.0", "Южная граница"
    assert result[1] == "80.0", "Северная граница"
    assert result[2] == "20.0", "Западная граница"
    assert result[3] == "180.0", "Восточная граница"

    # Проверка параметров запроса
    mock_get.assert_called_once()
    call_args = mock_get.call_args[1]
    assert call_args["params"]["q"] == "Russia"
    assert call_args["params"]["format"] == "json"
    assert call_args["params"]["limit"] == 1


@patch("requests.get")
def test_get_country_coordinates_not_found(mock_get):
    """Тест получения координат несуществующей страны"""

    # Настройка мока на пустой ответ
    mock_response = create_mock_response(200, [])
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api.get_country_coordinates("NonExistentCountry")

    assert result is None, "Для несуществующей страны должен вернуть None"


@patch("requests.get")
def test_get_country_coordinates_no_boundingbox(mock_get):
    """Тест получения координат без boundingbox"""

    # Настройка мока на ответ без boundingbox
    response_data = [{"place_id": 12345, "lat": "55.75", "lon": "37.62"}]
    mock_response = create_mock_response(200, response_data)
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api.get_country_coordinates("Russia")

    assert result is None, "Без boundingbox должен вернуть None"


def test_get_bounding_box():
    """Тест преобразования координат в формат OpenSky"""

    api = AeroplaneAPI()
    coordinates = ["40.0", "80.0", "20.0", "180.0"]

    result = api._get_bounding_box(coordinates)

    assert result == (40.0, 20.0, 80.0, 180.0), "Неправильное преобразование"
    assert all(isinstance(x, float) for x in result), "Все значения должны быть float"


@patch.object(AeroplaneAPI, "get_country_coordinates")
@patch("requests.get")
def test_get_aeroplanes_success(mock_get, mock_get_coordinates):
    """Тест успешного получения самолетов"""

    # Настройка моков
    mock_get_coordinates.return_value = ["40.0", "80.0", "20.0", "180.0"]
    mock_response = create_mock_response(200, create_mock_opensky_response())
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api.get_aeroplanes("Russia")

    # Проверки
    assert len(result) == 2, "Должно быть 2 самолета"
    assert result[0]["icao24"] == "abc123"
    assert result[0]["callsign"] == "AFL101  "
    assert result[0]["origin_country"] == "Russia"
    assert result[0]["longitude"] == 37.62
    assert result[0]["latitude"] == 55.75
    assert result[0]["baro_altitude"] == 10000.0
    assert result[0]["on_ground"] == False
    assert result[0]["velocity"] == 250.0

    assert result[1]["icao24"] == "def456"
    assert result[1]["callsign"] == "DLH202"
    assert result[1]["origin_country"] == "Germany"

    # Проверка параметров запроса к OpenSky
    mock_get.assert_called_once()
    call_args = mock_get.call_args[1]
    assert call_args["params"]["lamin"] == 40.0
    assert call_args["params"]["lomin"] == 20.0
    assert call_args["params"]["lamax"] == 80.0
    assert call_args["params"]["lomax"] == 180.0


@patch.object(AeroplaneAPI, "get_country_coordinates")
def test_get_aeroplanes_no_coordinates(mock_get_coordinates):
    """Тест получения самолетов без координат страны"""

    # Настройка мока на возврат None
    mock_get_coordinates.return_value = None

    api = AeroplaneAPI()
    result = api.get_aeroplanes("Russia")

    assert result == [], "Без координат должен вернуть пустой список"


@patch.object(AeroplaneAPI, "get_country_coordinates")
@patch("requests.get")
def test_get_aeroplanes_empty_response(mock_get, mock_get_coordinates):
    """Тест получения самолетов с пустым ответом от OpenSky"""

    # Настройка моков
    mock_get_coordinates.return_value = ["40.0", "80.0", "20.0", "180.0"]
    mock_response = create_mock_response(200, {"time": 1641234567, "states": None})
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api.get_aeroplanes("Russia")

    assert result == [], "При отсутствии states должен вернуть пустой список"


@patch.object(AeroplaneAPI, "get_country_coordinates")
@patch("requests.get")
def test_get_aeroplanes_api_error(mock_get, mock_get_coordinates):
    """Тест получения самолетов при ошибке OpenSky API"""

    # Настройка моков
    mock_get_coordinates.return_value = ["40.0", "80.0", "20.0", "180.0"]
    mock_response = create_mock_response(500, None)
    mock_get.return_value = mock_response

    api = AeroplaneAPI()
    result = api.get_aeroplanes("Russia")

    assert result == [], "При ошибке API должен вернуть пустой список"


def test_parse_aeroplane_data():
    """Тест парсинга данных о самолетах"""

    api = AeroplaneAPI()

    # Тестовые данные от OpenSky API
    states = [
        [
            "abc123",  # icao24
            "AFL101",  # callsign
            "Russia",  # origin_country
            1641234567,  # time_position
            1641234567,  # last_contact
            37.62,  # longitude
            55.75,  # latitude
            10000.0,  # baro_altitude
            False,  # on_ground
            250.0,  # velocity
            90.0,  # true_track
            0.0,  # vertical_rate
            [1, 2, 3],  # sensors
            11000.0,  # geo_altitude
            "1234",  # squawk
            False,  # spi
            0,  # position_source
        ],
        # Неполные данные (должны быть пропущены)
        ["abc456", "DLH202", "Germany"],  # только 3 поля
    ]

    result = api._parse_aeroplane_data(states)

    assert len(result) == 1, "Должен распарсить только полные данные"
    assert result[0]["icao24"] == "abc123"
    assert result[0]["callsign"] == "AFL101"
    assert result[0]["origin_country"] == "Russia"
    assert result[0]["longitude"] == 37.62
    assert result[0]["latitude"] == 55.75
    assert result[0]["baro_altitude"] == 10000.0
    assert result[0]["on_ground"] == False
    assert result[0]["velocity"] == 250.0
    assert result[0]["true_track"] == 90.0
    assert result[0]["vertical_rate"] == 0.0
    assert result[0]["sensors"] == [1, 2, 3]
    assert result[0]["geo_altitude"] == 11000.0
    assert result[0]["squawk"] == "1234"
    assert result[0]["spi"] == False
    assert result[0]["position_source"] == 0
