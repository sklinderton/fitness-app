async function registerUser(event) {
    event.preventDefault();
    const name = document.getElementById('name').value;
    const sex = document.getElementById('sex').value;
    const weight = document.getElementById('weight').value;
    const height = document.getElementById('height').value;
    const age = document.getElementById('age').value;

    try {
        const response = await fetch('http://localhost:8000/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, sex, weight, height, age })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
        } else {
            alert(`Error: ${result.detail}`);
        }
    } catch (error) {
        alert(`Error de conexión: ${error.message}`);
    }
}

async function checkActivity(event) {
    event.preventDefault();
    const city = document.getElementById('city').value;
    const activity = document.getElementById('activity').value;
    const user_id = document.getElementById('user_id').value;

    if (!city) {
        document.getElementById('result').innerHTML = `<p style="color:red">Por favor, ingresa una ciudad.</p>`;
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/api/check_activity', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city, activity, user_id })
        });
        const result = await response.json();

        if (response.ok) {
            const div = document.getElementById('result');
            div.innerHTML = `
                <h3>Recomendación para ${result.weather.city}</h3>
                <p>${result.recommendation}</p>
                <h4>Condiciones climáticas</h4>
                <p>Temperatura: ${result.weather.temperature}°C</p>
                <p>Humedad: ${result.weather.humidity}%</p>
                <p>Viento: ${result.weather.wind_speed} m/s</p>
                <p>Condición: ${result.weather.condition}</p>
                <p>Índice UV: ${result.weather.uv}</p>
                <p>Probabilidad de lluvia: ${result.weather.chance_of_rain}%</p>
            `;
        } else {
            document.getElementById('result').innerHTML = `<p style="color:red">Error: ${result.detail}</p>`;
        }
    } catch (error) {
        document.getElementById('result').innerHTML = `<p style="color:red">Error de conexión: ${error.message}</p>`;
    }
}

window.onload = async () => {
    document.getElementById('register-form').addEventListener('submit', registerUser);
    document.getElementById('activity-form').addEventListener('submit', checkActivity);

    try {
        const response = await fetch('http://localhost:8000/api/cleaned_data');
        const data = await response.json();
        const div = document.getElementById('cleaned-data');
        if (data.length === 0) {
            div.innerHTML = '<p>No hay datos climáticos procesados.</p>';
        } else {
            let html = '<table border="1"><tr><th>Ciudad</th><th>Temperatura (°C)</th><th>Humedad (%)</th><th>Viento (m/s)</th><th>Presión (mb)</th><th>Condición</th><th>UV</th><th>Prob. Lluvia (%)</th><th>Fecha</th></tr>';
            data.forEach(row => {
                html += `<tr>
                    <td>${row.city}</td>
                    <td>${row.temperature}</td>
                    <td>${row.humidity}</td>
                    <td>${row.wind_speed}</td>
                    <td>${row.pressure}</td>
                    <td>${row.condition}</td>
                    <td>${row.uv}</td>
                    <td>${row.chance_of_rain}</td>
                    <td>${new Date(row.query_date).toLocaleString()}</td>
                </tr>`;
            });
            html += '</table>';
            div.innerHTML = html;
        }
    } catch (error) {
        document.getElementById('cleaned-data').innerHTML = `<p style="color:red">Error al cargar datos: ${error.message}</p>`;
    }
};