# Introduction

This repository contains an API to request current weather data from OpenWeather API using the Fast API framework.

## Getting Started

### Pre requisites

This project requires that you have SQLite installed, if you are using Linux you can follow the instructions in the dockerfile. Otherwise, if you do not want to install it, you can always use Docker.

### Using Docker

1. The first step is to check if you have Docker installed and, if you are using Windows, check that you can build linux containers.

    ```console
        $ docker run hello-world
        Hello from Docker!
        This message shows that your installation appears to be working correctly.
        ...
    ```

2. Go to the root dir and build the image:

    ```console
        $ docker build -f Dockerfile -t api/weather .
        Sending build context to Docker daemon  911.4kB
        Step 1/11 : FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
        ...
        Successfully built f18c0d730cbb
        Successfully tagged cid-datalake/cep:dev
    ```

3. Get the API KEY from you account in [OpenWeather API](https://openweathermap.org/api).

4. Start the container by typing the following cmd by replacing the <WEATHER_API_KEY> with your API KEY:

    ```sh
        docker run -it -e WEATHER_API_KEY=<WEATHER_API_KEY> --name weather -p 8000:80 api/weather:latest
    ```

5. Check the docs at: http://localhost:8000/docs

### Running locally

1. Install the project packages:

    ```sh
        pip install -e .
    ```

2. Get the API KEY from you account in [OpenWeather API](https://openweathermap.org/api).

3. Set environment variabels (Linux):

    ```sh
        export WEATHER_API_KEY=<MY_API_KEY>
    ```

4. Run:

    ```sh
        uvicorn api.main:app
    ```

## Build and Test

To test the app, you must:

1. Install required packages:

    ```sh
        pip install .[test]
    ```

2. Run pytest

    ```sh
        pytest
    ```

3. If you want, you can run Tox:

    ```sh
        tox
    ```
