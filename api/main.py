from typing import Dict

from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from sqlalchemy import select

from . import schemas
from .database import database, engine
from .models import Base, UserRequest
from .tasks import GetWeatherBackgroundTask
from .utils import WeatherClient, get_cities

Base.metadata.create_all(bind=engine)

cities = get_cities()

task_pool: Dict[int, GetWeatherBackgroundTask] = {}

weather_client = WeatherClient()

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/", status_code=202)
async def populate_weather(user_request: schemas.UserRequest, background_tasks: BackgroundTasks):
    user_id = user_request.user_id
    query = select(UserRequest).where(UserRequest.user_id == user_id)
    exist = await database.fetch_one(query)

    if not exist:
        task = GetWeatherBackgroundTask(
            cities=cities,
            database=database,
            weather_client=weather_client,
            user_id=user_id,
        )
        background_tasks.add_task(task.run)
        task_pool[task.user_id] = task
        return {"message": "Background task started succesfully."}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"The 'user_id' {user_id} already exists.",
    )


@app.get("/{user_id}", summary="Get user task progress")
async def get_progress(user_id: int):
    task = task_pool.get(user_id, None)
    if task:
        return {"Progress": f"{task.progress} %"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
