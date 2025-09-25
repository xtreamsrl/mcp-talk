from datetime import datetime

import httpx
from mcp.server.fastmcp import FastMCP

from weather import API_KEY

mcp = FastMCP("weather-server")


@mcp.resource("weather://available_countries")
def get_available_countries() -> list[dict[str, str]]:
    return [
        {"code": "US", "name": "United States", "region": "North America"},
        {"code": "CA", "name": "Canada", "region": "North America"},
        {"code": "UK", "name": "United Kingdom", "region": "Europe"},
        {"code": "FR", "name": "France", "region": "Europe"},
    ]


@mcp.prompt()
def get_weather_suggestions(location: str, forecast: str) -> str:
    return f"""
I'm in {location} and the weather is {forecast}. What should I do?
    """


@mcp.tool("get_current_weather")
def get_current_weather(location: str):
    url = "http://api.openweathermap.org/data/2.5/weather"
    response = httpx.get(url, params={"q": location, "appid": API_KEY, "units": "metric"})
    data = response.json()
    _ = response.raise_for_status()
    return {
        "temperature": f"{data['main']['temp']}°C",
        "description": data['weather'][0]['description'],
        "humidity": f"{data['main']['humidity']}%",
        "wind": f"{data['wind']['speed']} m/s"
    }

@mcp.tool("get_weather_forecast")
def get_weather_forecast(location: str, days: int):
    url = "http://api.openweathermap.org/data/2.5/forecast"
    response = httpx.get(url, params={"q": location, "appid": API_KEY, "units": "metric"})
    data = response.json()
    _ = response.raise_for_status()

    daily = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        if date not in daily:
            daily[date] = []
        daily[date].append(item["main"]["temp"])
    forecast = []
    for i, (date, temps) in enumerate(daily.items()):
        if i >= days:
            break
    forecast.append({"date": date, "min": f"{min(temps)}°C", "max": f"{max(temps)}°C"})
    return {"forecast": forecast}

@mcp.tool("get_sun_times")
def get_sun_times(location: str):
    url = "http://api.openweathermap.org/data/2.5/weather"
    response = httpx.get(url, params={"q": location, "appid": API_KEY})
    data = response.json()
    _ = response.raise_for_status()

    return {
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S"),
        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")
    }

if __name__ == "__main__":
    # Initialize and run the local MCP server
    mcp.run(transport='stdio')