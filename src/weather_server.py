import random
from typing import Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")


@mcp.resource("weather://available_countries")
def get_available_countries() -> list[dict[str, str]]:
    return [
        {"code": "US", "name": "United States", "region": "North America"},
        {"code": "CA", "name": "Canada", "region": "North America"},
        {"code": "UK", "name": "United Kingdom", "region": "Europe"},
        {"code": "FR", "name": "France", "region": "Europe"},
    ]


@mcp.tool("get_current_weather")
def get_current_weather(
    location: str, unit: Literal["celsius", "fahrenheit"] = "celsius"
) -> dict[str, str | int]:
    return {
        "location": location,
        "temperature": random.randint(15, 30)
        if unit == "celsius"
        else random.randint(60, 85),
        "unit": unit,
        "forecast": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
    }
