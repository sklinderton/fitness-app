from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import httpx
from datetime import datetime
from typing import Literal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las orígenes (para pruebas locales)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Configuración de la base de datos MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Cambia por tu contraseña de MySQL
    'database': 'fitness_app'
}

# Clave de la API de WeatherAPI.com
WEATHER_API_KEY = 'b86b4847d2f349d9a4e210926250408'

# Lista de actividades al aire libre
ACTIVITIES = [
    'natación', 'correr', 'voleibol de playa', 'ciclismo', 'senderismo',
    'kayak', 'surf', 'tenis', 'escalada al aire libre', 'yoga al aire libre'
]

# Modelos Pydantic para validación de datos
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

# Función para obtener datos climáticos desde WeatherAPI.com
async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={city}&days=1&aqi=yes'
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        return None

# Evaluar si es seguro realizar la actividad según el clima
def evaluate_activity(weather_data, activity: str):
    current = weather_data['current']
    forecast_hour = weather_data['forecast']['forecastday'][0]['hour'][0]
    
    temp = current['temp_c']
    humidity = current['humidity']
    wind_speed = current['wind_kph'] / 3.6  # Convertir a m/s
    uv_index = current['uv']
    condition = current['condition']['text'].lower()
    chance_of_rain = forecast_hour['chance_of_rain']
    gust_speed = current['gust_kph'] / 3.6  # Convertir a m/s

    # Reglas para determinar si es seguro
    if 'rain' in condition or 'thunderstorm' in condition or chance_of_rain > 50:
        return f"No es recomendable practicar {activity} debido a {condition} o alta probabilidad de lluvia ({chance_of_rain}%)."
    if uv_index > 7:
        return f"Evita {activity} por alto índice UV ({uv_index}). Usa protector solar."
    if gust_speed > 15:
        return f"Las ráfagas de viento son muy fuertes ({gust_speed} m/s) para {activity}."
    if temp < 5 or temp > 35:
        return f"La temperatura ({temp}°C) no es ideal para {activity}."
    return f"¡Es un buen momento para practicar {activity}!"

@app.post('/api/register')
async def register_user(user: User):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
        INSERT INTO users (name, sex, weight, height, age)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user.name, user.sex, user.weight, user.height, user.age))
        conn.commit()
        cursor.close()
        conn.close()
        return {'message': 'Usuario registrado con éxito'}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(err)}")

@app.post('/api/check_activity')
async def check_activity(data: ActivityCheck):
    if data.activity not in ACTIVITIES:
        raise HTTPException(status_code=400, detail="Actividad no válida")
    
    weather_data = await get_weather(data.city)
    if not weather_data:
        raise HTTPException(status_code=400, detail=f"No se pudieron obtener los datos climáticos para {data.city}")

    recommendation = evaluate_activity(weather_data, data.activity)

    # Guardar consulta en la base de datos
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
        INSERT INTO queries (user_id, city, activity, recommendation, query_date)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (data.user_id, data.city, data.activity, recommendation, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(err)}")

    return {
        'recommendation': recommendation,
        'weather': {
            'city': weather_data['location']['name'],
            'temperature': weather_data['current']['temp_c'],
            'humidity': weather_data['current']['humidity'],
            'wind_speed': weather_data['current']['wind_kph'] / 3.6,
            'condition': weather_data['current']['condition']['text'],
            'uv': weather_data['current']['uv'],
            'chance_of_rain': weather_data['forecast']['forecastday'][0]['hour'][0]['chance_of_rain']
        }
    }

@app.get('/api/cleaned_data')
async def get_cleaned_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cleaned_weather")
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(err)}")