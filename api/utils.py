import os
from dataclasses import dataclass

import aiohttp
from aiolimiter import AsyncLimiter
from pydantic import BaseSettings


class Settings(BaseSettings):
    weather_api_key: str
    database_url: str


settings = Settings()


@dataclass
class CityWeather:
    city_id: int
    temperature: float
    humidity: float

    @classmethod
    def from_json(cls, json_data: dict) -> "CityWeather":
        temp = json_data["main"]["temp"]
        humidity = json_data["main"]["humidity"]
        city_id = json_data["id"]
        return CityWeather(city_id, temp, humidity)

    def to_json(self) -> dict:
        json_data = {
            "city_id": self.city_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
        }
        return json_data


def get_cities():
    cities = []
    here = os.path.abspath(os.path.dirname(__file__))
    with open(f"{here}/data/cities.txt", "r") as file:
        lines = file.read().splitlines()
        cities = [int(c.strip()) for l in lines for c in l.split(",")]
    return cities


class WeatherClient:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, max_rate=60, time_period=65) -> None:
        self.api_key = settings.weather_api_key
        self.rate_limit = AsyncLimiter(max_rate, time_period)

    async def get(self, http_session: aiohttp.ClientSession, city_id: int):
        params = {"id": city_id, "appid": self.api_key, "units": "metric"}
        async with self.rate_limit:
            async with http_session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    json_data = await response.json()
                    return CityWeather.from_json(json_data)
                response.raise_for_status()
