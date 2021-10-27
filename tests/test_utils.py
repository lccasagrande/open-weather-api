import os
from io import StringIO

import api.utils as utils
import pytest


@pytest.fixture
def json_data():
    return {
        "main": {
            "temp": 25,
            "humidity": 12,
        },
        "id": 1,
    }


def test_get_settings_returns_env_vars(mocker):
    utils.get_settings.cache_clear()
    env_vars = {
        "WEATHER_API_KEY": "api_key",
        "DATABASE_URL": "///.db",
    }
    mocker.patch.dict(os.environ, env_vars)
    settings = utils.get_settings()
    assert settings.weather_api_key == env_vars["WEATHER_API_KEY"]
    assert settings.database_url == env_vars["DATABASE_URL"]


class TestutilsSettings:
    def test_settigs_read_env_vars(self, mocker):
        env_vars = {
            "WEATHER_API_KEY": "api_key",
            "DATABASE_URL": "///.db",
        }

        mocker.patch.dict(os.environ, env_vars)

        settings = utils.Settings()

        assert settings.weather_api_key == env_vars["WEATHER_API_KEY"]
        assert settings.database_url == env_vars["DATABASE_URL"]


class TestutilsCityWeather:
    def test_from_json_parse(self, json_data):
        city_weather = utils.CityWeather.from_json(json_data)

        assert city_weather.temperature == 25
        assert city_weather.humidity == 12
        assert city_weather.city_id == 1

    def test_to_json_schema(self):
        city_weather = utils.CityWeather(1, 80, 10)

        json_data = city_weather.to_json()

        json_data["city_id"] = 1
        json_data["temperature"] = 80
        json_data["humidity"] = 10


def test_get_cities(mocker):
    mock_file = StringIO("1010,2020\n30,31")
    mocker.patch("api.utils.open", return_value=mock_file)

    cities = utils.get_cities()

    assert len(cities) == 4
    assert cities[0] == 1010
    assert cities[-1] == 31


class TestutilsWeatherClient:
    @pytest.mark.asyncio
    async def test_get_request_for_city_weather(self, mocker, json_data):
        mocker.patch("api.utils.AsyncLimiter", autospec=True)
        mock_setts = mocker.patch("api.utils.Settings")
        mock_setts.return_value.weather_api_key = "api_key"
        mocker.patch("api.utils.CityWeather", autospec=True)
        mock_sess = mocker.patch("api.utils.aiohttp.ClientSession", autospec=True)
        resp = mock_sess.get.return_value.__aenter__.return_value
        resp.json.return_value = json_data
        resp.status = 200

        client = utils.WeatherClient()

        await client.get(mock_sess, 10)

        params = {
            "id": 10,
            "appid": "api_key",
            "units": "metric",
        }

        mock_sess.get.assert_called_once_with(client.BASE_URL, params=params)

    @pytest.mark.asyncio
    async def test_get_return_city_weather(self, mocker, json_data):
        mocker.patch("api.utils.AsyncLimiter", autospec=True)
        mocker.patch("api.utils.Settings")
        mock_cweather = mocker.patch("api.utils.CityWeather", autospec=True)
        mock_sess = mocker.patch("api.utils.aiohttp.ClientSession", autospec=True)
        resp = mock_sess.get.return_value.__aenter__.return_value
        resp.json.return_value = json_data
        resp.status = 200

        client = utils.WeatherClient()

        r = await client.get(mock_sess, 10)

        mock_cweather.from_json.assert_called_once_with(json_data)
        assert r == mock_cweather.from_json.return_value

    @pytest.mark.asyncio
    async def test_get_raises_when_status_code_not_ok(self, mocker, json_data):
        mocker.patch("api.utils.AsyncLimiter", autospec=True)
        mocker.patch("api.utils.Settings")
        mocker.patch("api.utils.CityWeather", autospec=True)
        mock_sess = mocker.patch("api.utils.aiohttp.ClientSession", autospec=True)

        resp = mock_sess.get.return_value.__aenter__.return_value
        resp.json.return_value = json_data
        resp.status = 401
        client = utils.WeatherClient()

        await client.get(mock_sess, 10)

        resp.raise_for_status.assert_called_once()
