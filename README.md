# Aplicación Fitness al Aire Libre

Esta aplicación permite a los usuarios registrar sus datos personales, seleccionar una ciudad y una actividad al aire libre, y verificar si es seguro realizarla según las condiciones climáticas obtenidas de WeatherAPI.com. Utiliza un frontend HTML/JavaScript, un backend con FastAPI, un proceso ETL para datos climáticos, y una base de datos MySQL para almacenar usuarios, consultas y datos climáticos.

## Requisitos
- **Git**: Para clonar el repositorio.
- **Python 3.8+**: Para el backend y ETL.
- **MySQL**: Para la base de datos.
- **Navegador web**: Para probar el frontend.
- **WeatherAPI.com Key**: Incluida en el código (`b86b4847d2f349d9a4e210926250408`).

## Estructura del Proyecto
```
fitness-app/
├── backend/
│   ├── main.py          # Servidor FastAPI
│   ├── etl.py           # Proceso ETL para datos climáticos
│   ├── requirements.txt # Dependencias de Python
│   └── schema.sql       # Esquema de la base de datos
├── frontend/
│   ├── index.html       # Interfaz de usuario
│   ├── styles.css       # Estilos CSS
│   └── script.js        # Lógica del frontend
└── README.md
```

## Instalación y Ejecución
Sigue estos pasos para clonar y ejecutar la aplicación en tu máquina local.

### 1. Clonar el Repositorio
```bash
git clone https://github.com/USERNAME/fitness-app.git
cd fitness-app
```

### 2. Configurar MySQL
1. Asegúrate de que MySQL esté corriendo:
   ```bash
   mysqladmin -u root -p status
   ```
   Ingresa tu contraseña de MySQL. En Windows, inicia MySQL con XAMPP si es necesario.

2. Crea la base de datos y las tablas:
   ```bash
   mysql -u root -p < backend/schema.sql
   ```
   Esto crea la base de datos `fitness_app` y las tablas `users`, `raw_weather`, `cleaned_weather`, y `queries`.

3. Actualiza la contraseña de MySQL en:
   - `backend/main.py`
   - `backend/etl.py`
   Busca:
   ```python
   db_config = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_password',  # Reemplaza con tu contraseña de MySQL
       'database': 'fitness_app'
   }
   ```
   Guarda los archivos.

### 3. Instalar Dependencias
1. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. Instala las dependencias:
   ```bash
   pip install -r backend/requirements.txt
   ```

### 4. Correr el Backend
1. Inicia el servidor FastAPI:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Accede a `http://localhost:8000/docs` para probar los endpoints.

### 5. Correr el Proceso ETL
1. Pobla la tabla `cleaned_weather` con datos climáticos:
   ```bash
   python backend/etl.py --city "London"
   ```
   Repite para otras ciudades (por ejemplo, `Tokyo`).

2. Verifica los datos:
   ```bash
   mysql -u root -p
   ```
   ```sql
   USE fitness_app;
   SELECT * FROM cleaned_weather;
   ```

### 6. Probar la Aplicación
1. **Registrar un usuario**:
   - En el frontend, completa el formulario de registro (Nombre, Sexo, Peso, Altura, Edad).
   - Haz clic en "Registrar". Verifica:
     ```sql
     SELECT * FROM users;
     ```

2. **Consultar una actividad**:
   - Ingresa una ciudad (por ejemplo, "Tokyo"), selecciona una actividad (por ejemplo, "ciclismo"), y usa el ID del usuario registrado.
   - Haz clic en "Consultar". Verás una recomendación basada en el clima en tiempo real.
   - Verifica:
     ```sql
     SELECT * FROM queries;
     ```

3. **Ver datos climáticos**:
   - Usa `http://localhost:8000/docs` para probar `GET /api/cleaned_data`, que muestra datos de ciudades procesadas por el ETL.

## Notas
- **Ciudades**: El frontend consulta cualquier ciudad válida mediante WeatherAPI.com en tiempo real (`/api/check_activity`). El ETL solo guarda datos de ciudades específicas en `cleaned_weather`.
