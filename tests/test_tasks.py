import pytest
from api.tasks import GetWeatherBackgroundTask


def raise_exception():
    raise Exception()


class TestGetWeatherBackgroundTask:
    @pytest.mark.asyncio
    async def test_run_persist_date(self, mocker):
        mocker.patch("api.utils.aiohttp.ClientSession", autospec=True)
        mock_db = mocker.AsyncMock()
        mock_client = mocker.patch("api.tasks.WeatherClient", autospec=True)
        cities = [1, 2, 3]
        user_id = 1

        task = GetWeatherBackgroundTask(cities, mock_db, mock_client, user_id)

        await task.run()

        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_retry_attemps(self, mocker):
        mock_sess = mocker.patch("api.utils.aiohttp.ClientSession", autospec=True)
        mock_db = mocker.AsyncMock()
        mock_client = mocker.patch("api.tasks.WeatherClient", autospec=True)
        mock_sess.side_effect = [raise_exception, mocker.AsyncMock()]
        cities = [1, 2, 3]
        user_id = 1

        task = GetWeatherBackgroundTask(cities, mock_db, mock_client, user_id)

        await task.run()

        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_raises_when_retry_exceed(self, mocker):
        mock_sess = mocker.patch("api.utils.aiohttp.ClientSession")
        mock_db = mocker.AsyncMock()
        mock_client = mocker.patch("api.tasks.WeatherClient", autospec=True)
        mock_sess.return_value.__aenter__.side_effect = raise_exception
        cities = [1, 2, 3]
        user_id = 1

        task = GetWeatherBackgroundTask(cities, mock_db, mock_client, user_id)

        with pytest.raises(Exception) as _:
            await task.run()

        task.status == "Finished"

    @pytest.mark.asyncio
    async def test_progress(self, mocker):
        mocker.patch("api.utils.aiohttp.ClientSession", autospec=True)
        mock_db = mocker.AsyncMock()
        mock_client = mocker.patch("api.tasks.WeatherClient", autospec=True)
        cities = [1, 2, 3]
        user_id = 1

        task = GetWeatherBackgroundTask(cities, mock_db, mock_client, user_id)
        assert task.progress == 0
        await task.run()
        assert task.progress == 100
