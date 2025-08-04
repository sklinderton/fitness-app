async function registerUser() {
    const name = document.getElementById('name').value;
    const sex = document.getElementById('sex').value;
    const weight = document.getElementById('weight').value;
    const height = document.getElementById('height').value;
    const age = document.getElementById('age').value;

    const response = await fetch('http://localhost:5000/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, sex, weight, height, age })
    });
    const result = await response.json();
    alert(result.message);
}

async function checkActivity() {
    const city = document.getElementById('city').value;
    const activity = document.getElementById('activity').value;
    const user_id = document.getElementById('user_id').value;

    const response = await fetch('http://localhost:5000/api/check_activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city, activity, user_id })
    });
    const result = await response.json();

    if (response.ok) {
        const div = document.getElementById('result');
        div.innerHTML = `
            <h3>Recomendación</h3>
            <p>${result.recommendation}</p>
            <h4>Condiciones climáticas</h4>
            <p>Temperatura: ${result.weather.temperature}°C</p>
            <p>Humedad: ${result.weather.humidity}%</p>
            <p>Viento: ${result.weather.wind_speed} m/s</p>
            <p>Condición: ${result.weather.condition}</p>
        `;
    } else {
        document.getElementById('result').innerHTML = `<p style="color:red">${result.error}</p>`;
    }
}

// Actualizar datos al cargar la página
window.onload = async () => {
    const response = await fetch('http://localhost:5000/api/cleaned_data');
    const data = await response.json();
    console.log('Datos limpios:', data);  // Mostrar en consola para depuración
};