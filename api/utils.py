"""Utilities for handling env vars and API requests."""
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List

import aiohttp
from aiolimiter import AsyncLimiter
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Stores env vars.

    Attributes:
        weather_api_key: the Open Weather API Key.
        database_url: the URL to connect to the database.
    """

    weather_api_key: str = ""
    database_url: str = "sqlite:///./sql_app.db"


@lru_cache()
def get_settings() -> Settings:
    """Return settings from cache."""
    return Settings()


@dataclass
class CityWeather:
    """Stores city weather data.

    Attributes:
        city_id: the id of the city.
        temperature: the temperature in Celsius.
        humidity: the city humidity.
    """

    city_id: int
    temperature: float
    humidity: float

    @classmethod
    def from_json(cls, json_data: dict) -> "CityWeather":
        """Creates a CityWeather instace from the OpenWeather API JSON.

        Args:
            json_data: the JSON following the OpenWeather format.

        Returns:
            An instance of the CityWeather class.
        """
        temp = json_data["main"]["temp"]
        humidity = json_data["main"]["humidity"]
        city_id = json_data["id"]
        return CityWeather(city_id, temp, humidity)

    def to_json(self) -> dict:
        """Convert CityWeather to JSON.

        Returns:
            A dict with city weather data.
        """
        json_data = {
            "city_id": self.city_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
        }
        return json_data


def get_cities() -> List[int]:
    """Load cities from file.

    Returns:
        A list with cities id.
    """
    cities = []
    here = os.path.abspath(os.path.dirname(__file__))
    with open(f"{here}/data/cities.txt", "r") as file:
        lines = file.read().splitlines()
        cities = [int(city.strip()) for ln in lines for city in ln.split(",")]
    return cities


class WeatherClient:
    """Client to handle OpenWeather API requests."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, max_rate=60, time_period=65) -> None:
        """A client to request for city weather.

        Args:
            max_rate: Max number of requests before blocking.
            time_period: time period in which to limit the rate of requests.

        Attributes:
            BASE_URL: OpenWeather API base url.
        """
        self.api_key = get_settings().weather_api_key
        self.rate_limit = AsyncLimiter(max_rate, time_period)

    async def get(
        self, http_session: aiohttp.ClientSession, city_id: int
    ) -> CityWeather:
        """Get city weather from OpenWeather API.

        Args:
            http_session: the HTTP session to use to request data.
            city_id: the ID of the city.

        Returns:
            An instance of the City Weather with the latest weather data.
        """
        params = {"id": city_id, "appid": self.api_key, "units": "metric"}
        async with self.rate_limit:
            async with http_session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    json_data = await response.json()
                    return CityWeather.from_json(json_data)
                await response.raise_for_status()
