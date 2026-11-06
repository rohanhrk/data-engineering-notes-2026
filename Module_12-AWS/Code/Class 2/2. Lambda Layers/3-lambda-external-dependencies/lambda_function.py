"""
AWS Lambda External Dependencies Demo — City Weather Service

Just send a city name → get weather info back.
Shows how to use an external package (requests) in Lambda.
"""

import json
import requests

"""
{
    "city": "Mumbai"
}
"""

def lambda_handler(event, context):
    print(f"Received event: {event}")

    # Step 1: Basic input validation
    city = event.get("city", "").strip()
    if not city:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing 'city' in the request"})
        }

    # Step 2: Convert city name to coordinates (Geocoding API - free, no key needed)
    geo_response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
        timeout=5,
    )
    geo_data = geo_response.json()

    results = geo_data.get("results", [])
    print(f"Geocoded Response: {geo_response.json()}")
    if not results:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": f"City '{city}' not found"})
        }

    location = results[0]
    lat = location["latitude"]
    lon = location["longitude"]
    country = location.get("country", "Unknown")

    print(f"Geocoded: {city} → {country} ({lat}, {lon})")

    # Step 3: Fetch weather using coordinates (Weather API - free, no key needed)
    weather_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "daily": "sunrise,sunset",
            "timezone": "auto",
        },
        timeout=5,
    )
    weather_data = weather_response.json()
    print(f"Weather Response: {weather_response.json()}")
    current = weather_data.get("current_weather", {})
    daily = weather_data.get("daily", {})

    # Step 4: Return the result
    return {
        "statusCode": 200,
        "body": json.dumps({
            "city": location.get("name", city),
            "country": country,
            "coordinates": {"latitude": lat, "longitude": lon},
            "temperature_celsius": current.get("temperature"),
            "wind_speed_kmh": current.get("windspeed"),
            "local_time": current.get("time"),
            "sunrise": daily.get("sunrise", [None])[0],
            "sunset": daily.get("sunset", [None])[0],
        })
    }
