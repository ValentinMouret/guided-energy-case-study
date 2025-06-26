"""
The weather module implements the OpenWeather API and exposes it as a tool to be used by the LLM.

Two endpoints are implemented:
- https://openweathermap.org/api/one-call-3, which returns the weather forecast for (lat, lon) coordinates.
- https://openweathermap.org/api/geocoding-api, which guesses the coordinates of a location.

The tool that is exposed to the LLM accepts only a location (e.g. "Paris").
That’s because we expect users to be querying using location names and not coordinates.

Reference: https://openweathermap.org
"""

from __future__ import annotations

from datetime import date
from typing import Literal, NewType

import requests
from anthropic.types import ToolParam
from pydantic import BaseModel

from .config import config

Unit = Literal["metric", "imperial"]

Lat = NewType("Lat", float)
Lon = NewType("Lon", float)


def validate_lat(value: float) -> Lat:
    if -90 <= value <= 90:
        return Lat(value)
    raise ValueError("Expected latitude to be between -90 and 90.")


def validate_lon(value: float) -> Lon:
    if -180 <= value <= 180:
        return Lon(value)
    raise ValueError("Expected longitude to be between -180 and 180.")


class Coordinates(BaseModel):
    lat: Lat
    lon: Lon


class CoordinatesResponse(BaseModel):
    name: str
    lat: Lat
    lon: Lon


def __get_coordinates(location: str) -> Coordinates:
    response = requests.get(
        "https://api.openweathermap.org/geo/1.0/direct",
        params={
            "appid": config.weather_api_key,
            "q": location,
            "limit": 1,
        },
    )
    response.raise_for_status()

    data = response.json()
    if not isinstance(data, list):
        raise ValueError("Geocoding API error: expected response to be a list")

    if not len(data) == 1:
        raise ValueError("Geocoding API error: expected exactly one item in response")

    best_match = CoordinatesResponse.model_validate(data[0])

    return Coordinates(
        lat=validate_lat(best_match.lat),
        lon=validate_lon(best_match.lon),
    )


class Temperatures(BaseModel):
    day: float  # Average
    min: float
    max: float


class DailyWeather(BaseModel):
    # Extract more fields here as it becomes necessary.
    dt: int
    summary: str
    temp: Temperatures
    clouds: float
    rain: float | None = None
    uvi: float

    def simplify(self, offset: int):
        """
        The data returned by the API needs to be transformed before being fed to the LLM for two reasons:
        1. limiting the data diminishes the complexity and increases the odds that the LLM uses meaningful data.
        2. some values need to be updated to be more useful to the LLM. For example, `dt` as a timestamp
           is processed to include the timezone offset and be returned as a simple date string.
        """
        return {
            "date": str(date.fromtimestamp(self.dt + offset)),
            "summary": self.summary,
            "temp": self.temp.model_dump(),
            "clouds": self.clouds,
            "rain": self.rain,
            "uvi": self.uvi,
        }


class WeatherResponse(BaseModel):
    timezone_offset: int
    daily: list[DailyWeather]

    def simplify(self):
        return {"daily": [d.simplify(self.timezone_offset) for d in self.daily]}


def __get_weather(coordinates: Coordinates) -> WeatherResponse:
    request = requests.get(
        "https://api.openweathermap.org/data/3.0/onecall",
        params={
            "lat": coordinates.lat,
            "lon": coordinates.lon,
            "appid": config.weather_api_key,
            "units": "metric",  # Can be improved.
        },
    )
    request.raise_for_status()
    return WeatherResponse.model_validate_json(request.text)


def get_weather(location: str) -> WeatherResponse:
    coordinates = __get_coordinates(location)
    return __get_weather(coordinates)


get_weather_tool: ToolParam = {
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "Place we want the weather for",
            },
        },
        "required": ["location"],
    },
}


class GetWeatherInputs(BaseModel):
    location: str

    @staticmethod
    def from_tool_call(input: object) -> GetWeatherInputs:
        if not isinstance(input, dict):
            raise ValueError("Tool call error: wrong inputs")

        return GetWeatherInputs.model_validate(input)
