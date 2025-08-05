from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import httpx
from datetime import datetime
from typing import Literal
from contextlib import closing
import os

# Crear instancia de FastAPI
app = FastAPI()

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'junior123',
    'database': 'fitness_app',
    'pool_name': 'fitness_pool',
    'pool_size': 5
}

# Clave de la API de WeatherAPI.com
WEATHER_API_KEY = 'b86b4847d2f349d9a4e210926250408'

# Lista de actividades al aire libre
ACTIVITIES = [
    'natación', 'correr', 'voleibol de playa', 'ciclismo', 'senderismo',
    'kayak', 'surf', 'tenis', 'escalada al aire libre', 'yoga al aire libre'
]


# Crear pool de conexiones al iniciar
@app.on_event("startup")
def startup_db():
    try:
        # Crear pool de conexiones
        mysql.connector.connect(**DB_CONFIG)
        print("✅ Pool de conexiones a MySQL creado")
    except mysql.connector.Error as err:
        print(f"❌ Error al conectar con MySQL: {err}")
        # Salir si no hay conexión a la base de datos
        os._exit(1)


# Modelos Pydantic
class User(BaseModel):
    name: str
    sex: Literal['M', 'F', 'Other']
    weight: float
    height: float
    age: int


class ActivityCheck(BaseModel):
    city: str
    activity: str
    user_id: int


# Obtener conexión de la base de datos
def get_db_connection():
    try:
        return mysql.connector.connect(pool_name='fitness_pool')
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión a la base de datos: {err}"
        )


# Obtener datos climáticos
async def get_weather(city: str):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=yes'
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as err:
            raise HTTPException(
                status_code=500,
                detail=f"Error de conexión con WeatherAPI: {str(err)}"
            )
        except httpx.HTTPStatusError as err:
            raise HTTPException(
                status_code=err.response.status_code,
                detail=f"WeatherAPI respondió con error: {str(err)}"
            )


# Evaluar seguridad de la actividad
def evaluate_activity(weather_data, activity: str):
    current = weather_data['current']
    forecast = weather_data['forecast']['forecastday'][0]

    # Usar datos de la hora actual o la próxima hora
    current_hour = datetime.now().hour
    forecast_hour = next(
        (hour for hour in forecast['hour'] if hour['time'].startswith(f"{current_hour:02d}")),
        forecast['hour'][0]
    )

    temp = current['temp_c']
    humidity = current['humidity']
    wind_speed = current['wind_kph'] / 3.6  # Convertir a m/s
    uv_index = current['uv']
    condition = current['condition']['text'].lower()
    chance_of_rain = forecast_hour['chance_of_rain']
    gust_speed = current['gust_kph'] / 3.6  # Convertir a m/s

    # Reglas de seguridad
    if 'rain' in condition or 'thunderstorm' in condition or chance_of_rain > 50:
        return f"No es recomendable practicar {activity} debido a {condition} o alta probabilidad de lluvia ({chance_of_rain}%)."
    if uv_index > 7:
        return f"Evita {activity} por alto índice UV ({uv_index}). Usa protector solar."
    if gust_speed > 15:
        return f"Las ráfagas de viento son muy fuertes ({gust_speed:.1f} m/s) para {activity}."
    if temp < 5 or temp > 35:
        return f"La temperatura ({temp}°C) no es ideal para {activity}."
    return f"¡Es un buen momento para practicar {activity}!"


# Endpoint para registrar usuario
@app.post('/api/register')
async def register_user(user: User):
    with closing(get_db_connection()) as conn:
        with closing(conn.cursor()) as cursor:
            try:
                query = """
                INSERT INTO users (name, sex, weight, height, age)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    user.name,
                    user.sex,
                    user.weight,
                    user.height,
                    user.age
                ))
                conn.commit()
                return {'message': 'Usuario registrado con éxito', 'user_id': cursor.lastrowid}
            except mysql.connector.Error as err:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error en la base de datos: {str(err)}"
                )


# Endpoint para verificar actividad
@app.post('/api/check_activity')
async def check_activity(data: ActivityCheck):
    if data.activity not in ACTIVITIES:
        raise HTTPException(
            status_code=400,
            detail=f"Actividad no válida. Opciones válidas: {', '.join(ACTIVITIES)}"
        )

    try:
        weather_data = await get_weather(data.city)
    except HTTPException as he:
        # Guardar error en base de datos
        with closing(get_db_connection()) as conn:
            with closing(conn.cursor()) as cursor:
                query = """
                INSERT INTO queries (user_id, city, activity, recommendation, query_date)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data.user_id,
                    data.city,
                    data.activity,
                    f"Error al obtener datos climáticos: {he.detail}",
                    datetime.now()
                ))
                conn.commit()
        raise he

    recommendation = evaluate_activity(weather_data, data.activity)

    with closing(get_db_connection()) as conn:
        with closing(conn.cursor()) as cursor:
            try:
                query = """
                INSERT INTO queries (user_id, city, activity, recommendation, query_date)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data.user_id,
                    data.city,
                    data.activity,
                    recommendation,
                    datetime.now()
                ))
                conn.commit()
            except mysql.connector.Error as err:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al guardar consulta: {str(err)}"
                )

    return {
        'recommendation': recommendation,
        'weather': {
            'temperature': weather_data['current']['temp_c'],
            'humidity': weather_data['current']['humidity'],
            'wind_speed': weather_data['current']['wind_kph'] / 3.6,
            'condition': weather_data['current']['condition']['text'],
            'uv': weather_data['current']['uv'],
            'chance_of_rain': weather_data['forecast']['forecastday'][0]['hour'][0]['chance_of_rain']
        }
    }


# Endpoint para obtener datos limpios
@app.get('/api/cleaned_data')
async def get_cleaned_data():
    with closing(get_db_connection()) as conn:
        with closing(conn.cursor(dictionary=True)) as cursor:
            try:
                cursor.execute("SELECT * FROM cleaned_weather")
                return cursor.fetchall()
            except mysql.connector.Error as err:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error al obtener datos: {str(err)}"
                )


# Punto de entrada principal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,  # Cambiado de "main:app" a app
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )