#!/bin/bash

docker run -it \
  -e ANTHROPIC_API_KEY="your-anthropic-api-key" \
  -e WEATHER_API_KEY="your-openweathermap-api-key" \
  weather-assistant
