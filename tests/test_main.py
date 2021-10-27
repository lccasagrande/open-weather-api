from fastapi.testclient import TestClient
import pytest
from api.main import app, task_pool


@pytest.fixture
def app_client():
    return TestClient(app)


def test_populate_weather_raise_when_exists(mocker, app_client):
    mock_db = mocker.patch("api.main.database")
    mock_db.fetch_one = mocker.AsyncMock(return_value=True)

    r = app_client.post("/", json={"user_id": 1})

    assert r.status_code == 400


def test_populate_weather_create_background_task(mocker, app_client):
    mock_db = mocker.patch("api.main.database")
    mock_task = mocker.patch("api.main.GetWeatherBackgroundTask")
    mock_db.fetch_one = mocker.AsyncMock(return_value=False)

    r = app_client.post("/", json={"user_id": 1})

    mock_task.assert_called_once()
    assert len(task_pool) == 1
    assert r.status_code == 202


def test_get_progress_raises_when_not_found(mocker, app_client):

    r = app_client.get("/1")

    assert r.status_code == 404


def test_get_progress(mocker, app_client):
    mock_task = mocker.patch("api.main.GetWeatherBackgroundTask")
    task_pool[1] = mock_task

    r = app_client.get("/1")
    dt = r.json()

    assert r.status_code == 200
    assert dt["Progress"] == f"{mock_task.progress} %"


def test_app_on_startup_connects_to_db(mocker):
    mock_db = mocker.patch("api.main.database")
    mock_db.connect = mocker.AsyncMock()
    mock_db.disconnect = mocker.AsyncMock()

    with TestClient(app) as _:
        mock_db.connect.assert_called_once()
    mock_db.disconnect.assert_called_once()
