import mysql.connector
import httpx
from datetime import datetime

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Cambia por tu contraseña de MySQL
    'database': 'fitness_app'
}

# Clave de la API de WeatherAPI.com
WEATHER_API_KEY = 'b86b4847d2f349d9a4e210926250408'

# Función para obtener datos climáticos (Extract)
async def extract_weather(city='San Jose'):
    async with httpx.AsyncClient() as client:
        url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=yes'
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
            
        return None

# Función para transformar datos (Transform)
def transform_weather(weather_data):
    if not weather_data or 'current' not in weather_data or 'forecast' not in weather_data:
        return None
    try:
        current = weather_data['current']
        forecast_hour = weather_data['forecast']['forecastday'][0]['hour'][0]
        return {
            'city': weather_data['location']['name'],
            'temperature': current['temp_c'],
            'humidity': current['humidity'],
            'wind_speed': current['wind_kph'] / 3.6,  # Convertir a m/s
            'pressure': current['pressure_mb'],
            'condition': current['condition']['text'],
            'uv': current['uv'],
            'chance_of_rain': forecast_hour['chance_of_rain'],
            'query_date': datetime.now()
        }
    except KeyError:
        return None

# Función para cargar datos en la tabla CLEANED (Load)
def load_weather(cleaned_data):
    if not cleaned_data:
        return
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = """
    INSERT INTO cleaned_weather (city, temperature, humidity, wind_speed, pressure, weather_condition, uv, chance_of_rain, query_date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (
        cleaned_data['city'], cleaned_data['temperature'], cleaned_data['humidity'],
        cleaned_data['wind_speed'], cleaned_data['pressure'], cleaned_data['condition'],
        cleaned_data['uv'], cleaned_data['chance_of_rain'], cleaned_data['query_date']
    ))
    conn.commit()
    cursor.close()
    conn.close()

# Función para respaldar datos
def backup_raw_weather(weather_data):
    if not weather_data:
        return
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = """
    INSERT INTO raw_weather (raw_data, query_date)
    VALUES (%s, %s)
    """
    cursor.execute(query, (str(weather_data), datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

# Proceso ETL completo
async def run_etl():
    weather_data = await extract_weather()
    backup_raw_weather(weather_data)  # Respaldar datos crudos
    cleaned_data = transform_weather(weather_data)
    load_weather(cleaned_data)

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_etl())