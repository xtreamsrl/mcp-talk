import httpx
from datetime import datetime

API_KEY = "..."

def resolve_coordinates(location: str):
    url = "http://api.openweathermap.org/data/2.5/weather"
    response = httpx.get(url, params={"q": location, "appid": API_KEY})
    
    _ = response.raise_for_status()

    data = response.json()
    return data["coord"]["lat"], data["coord"]["lon"]

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

def get_sun_times(location: str):
    url = "http://api.openweathermap.org/data/2.5/weather"
    response = httpx.get(url, params={"q": location, "appid": API_KEY})
    data = response.json()
    _ = response.raise_for_status()

    return {
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S"),
        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")
    }
