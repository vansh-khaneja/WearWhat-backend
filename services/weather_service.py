import requests
from typing import Optional
from datetime import datetime, date
from config import OPENWEATHERMAP_API_KEY


class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

    @staticmethod
    def get_weather_forecast(lat: float, lon: float, target_date: Optional[str] = None) -> dict:
        """
        Get weather forecast for given coordinates, optionally filtered by date.

        Args:
            lat: Latitude
            lon: Longitude
            target_date: Optional date in YYYY-MM-DD format (defaults to today)

        Returns:
            Dict with weather data including avg temperature and conditions
        """
        if not OPENWEATHERMAP_API_KEY:
            return {
                "success": False,
                "message": "Weather API key not configured"
            }

        try:
            params = {
                "lat": lat,
                "lon": lon,
                "appid": OPENWEATHERMAP_API_KEY,
                "units": "metric",  # Celsius
                "cnt": 40  # 5 days of data (8 per day, every 3 hours)
            }

            response = requests.get(WeatherService.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract weather data from forecast
            forecasts = data.get("list", [])
            if not forecasts:
                return {
                    "success": False,
                    "message": "No forecast data available"
                }

            # Parse target date or use today
            if target_date:
                try:
                    parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid date format. Use YYYY-MM-DD"
                    }
            else:
                parsed_date = date.today()

            # Filter forecasts for the target date
            date_forecasts = [
                f for f in forecasts
                if datetime.fromtimestamp(f["dt"]).date() == parsed_date
            ]

            # If no forecasts for target date, check if date is too far in future
            if not date_forecasts:
                # Check if target date is within forecast range
                available_dates = set(
                    datetime.fromtimestamp(f["dt"]).date() for f in forecasts
                )
                if parsed_date < min(available_dates):
                    # Use today's data if requested date is in the past
                    date_forecasts = [
                        f for f in forecasts
                        if datetime.fromtimestamp(f["dt"]).date() == min(available_dates)
                    ]
                    parsed_date = min(available_dates)
                elif parsed_date > max(available_dates):
                    return {
                        "success": False,
                        "message": f"Date {target_date} is beyond forecast range. Max available: {max(available_dates)}"
                    }

            if not date_forecasts:
                return {
                    "success": False,
                    "message": f"No forecast data available for {parsed_date}"
                }

            # Calculate stats for the target date
            temps = [f["main"]["temp"] for f in date_forecasts]
            avg_temp = round(sum(temps) / len(temps), 1)
            min_temp = round(min(temps), 1)
            max_temp = round(max(temps), 1)

            # Get most common weather condition for the day
            conditions = [f["weather"][0]["main"] for f in date_forecasts]
            most_common_condition = max(set(conditions), key=conditions.count)

            # Get midday forecast for representative values (or first available)
            midday_forecast = None
            for f in date_forecasts:
                hour = datetime.fromtimestamp(f["dt"]).hour
                if 11 <= hour <= 14:
                    midday_forecast = f
                    break
            if not midday_forecast:
                midday_forecast = date_forecasts[0]

            description = midday_forecast["weather"][0]["description"]
            icon = midday_forecast["weather"][0]["icon"]

            # Determine season suggestion based on temperature
            season_suggestion = WeatherService._get_season_suggestion(avg_temp)

            return {
                "success": True,
                "date": str(parsed_date),
                "location": {
                    "city": data.get("city", {}).get("name", "Unknown"),
                    "country": data.get("city", {}).get("country", ""),
                    "lat": lat,
                    "lon": lon
                },
                "current": {
                    "temp": round(midday_forecast["main"]["temp"], 1),
                    "feels_like": round(midday_forecast["main"]["feels_like"], 1),
                    "humidity": midday_forecast["main"]["humidity"],
                    "condition": midday_forecast["weather"][0]["main"],
                    "description": description,
                    "icon": f"https://openweathermap.org/img/wn/{icon}@2x.png"
                },
                "forecast": {
                    "avg_temp": avg_temp,
                    "min_temp": min_temp,
                    "max_temp": max_temp,
                    "dominant_condition": most_common_condition
                },
                "suggestion": season_suggestion
            }

        except requests.exceptions.RequestException as e:
            print(f"[WEATHER SERVICE] Error fetching weather: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to fetch weather data: {str(e)}"
            }

    @staticmethod
    def _get_season_suggestion(avg_temp: float) -> str:
        """Get clothing season suggestion based on temperature."""
        if avg_temp >= 30:
            return "summer"
        elif avg_temp >= 20:
            return "spring/fall"
        elif avg_temp >= 10:
            return "fall/winter"
        else:
            return "winter"

    @staticmethod
    def get_weather_by_city(city: str, country_code: Optional[str] = None, target_date: Optional[str] = None) -> dict:
        """
        Get weather forecast by city name, optionally filtered by date.

        Args:
            city: City name
            country_code: Optional 2-letter country code (e.g., "US", "IN")
            target_date: Optional date in YYYY-MM-DD format (defaults to today)

        Returns:
            Dict with weather data
        """
        if not OPENWEATHERMAP_API_KEY:
            return {
                "success": False,
                "message": "Weather API key not configured"
            }

        try:
            # First get coordinates from city name using geocoding
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"
            q = f"{city},{country_code}" if country_code else city
            geo_params = {
                "q": q,
                "limit": 1,
                "appid": OPENWEATHERMAP_API_KEY
            }

            geo_response = requests.get(geo_url, params=geo_params)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data:
                return {
                    "success": False,
                    "message": f"City '{city}' not found"
                }

            lat = geo_data[0]["lat"]
            lon = geo_data[0]["lon"]

            return WeatherService.get_weather_forecast(lat, lon, target_date)

        except requests.exceptions.RequestException as e:
            print(f"[WEATHER SERVICE] Error fetching weather by city: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to fetch weather data: {str(e)}"
            }
