import os
from typing import Literal

import httpx


def get_current_weather(
    latitude: float,
    longitude: float,
    api_key: str,
    units: Literal["imperial", "metric"] = "metric",
) -> dict[str, str | int]:
    base_url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": latitude,
        "lon": longitude,
        "units": units,
        "exclude": "minutely,hourly,daily",
        "appid": api_key,
    }
    return httpx.get(base_url, params=params).json()


if __name__ == "__main__":
    weather = get_current_weather(
        45.47794032288698, 9.142334791414777, os.getenv("OPENWEATHER_API_KEY")
    )
    print(weather)
