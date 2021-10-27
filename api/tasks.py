"""Background tasks for handling API requests."""
import asyncio
from datetime import datetime
from typing import Any, List
import aiohttp

from sqlalchemy import insert

from .models import UserRequest
from .utils import CityWeather, WeatherClient


class GetWeatherBackgroundTask:
    """Background task to handle weather requests."""

    def __init__(
        self,
        cities: List[int],
        database: Any,
        weather_client: WeatherClient,
        user_id: int,
        retry_total=3,
    ) -> None:
        """Task to get city weather and store it.

        Args:
            cities: a list with city ids.
            database: the database session to store the weather data.
            weather_client: the weather client to request for weather data.
            user_id: the user id.
            retry_total: total number of request retries.
        """
        self.user_id = user_id
        self.weather_client = weather_client
        self.database = database
        self.cities = cities
        self.retry_total = retry_total
        self._n_coroutines = 0
        self._progress = 0
        self.status = "Created"

    @property
    def progress(self) -> float:
        """Return the task progress."""
        if self._n_coroutines > 0:
            return round(self._progress / float(self._n_coroutines) * 100, 2)
        return 0

    async def _get_cities_weather(self, cities_id: List[int]) -> List[CityWeather]:
        """Request the city weather.

        Args:
            cities_id: a list with the cities id.

        Returns:
            a list with cities weather
        """
        self._n_coroutines = len(cities_id)
        cities_weather: List[CityWeather] = []

        async with aiohttp.ClientSession() as session:
            tasks = [self.weather_client.get(session, city_id) for city_id in cities_id]

            for task in asyncio.as_completed(tasks):
                weather = await task
                cities_weather.append(weather)
                self._progress += 1
                print(f"{self._progress} out of {self._n_coroutines}")

        return cities_weather

    async def run(self) -> None:
        """Run the task.

        It will request for city weather and store it in database.

        """
        self.status = "Running"
        request_time = datetime.utcnow()

        # Get cities
        retry, cities_weather, exc = 0, None, None
        while retry < self.retry_total and not cities_weather:
            try:
                cities_weather = await self._get_cities_weather(self.cities)
            except Exception as exc:
                retry += 1
                exc = exc

        if not cities_weather:
            self.status = "Error"
            raise exc or Exception("Service unavailable")

        # Insert in DB
        await self.database.execute(
            query=insert(UserRequest),
            values={
                "user_id": self.user_id,
                "request_time": request_time,
                "data": [c.to_json() for c in cities_weather],
            },
        )
        self.status = "Finished"
