from flask import Flask, render_template, request
import requests
import pandas as pd
import os

app = Flask(__name__, static_folder='static')

BASE_URL = "https://api.open-meteo.com/v1/forecast"
CITIES_FILE = os.path.join(app.static_folder, 'worldcities.xlsx')

def get_coordinates(city_name):
    """Fetch latitude and longitude of a city from the Excel file."""
    try:
        df = pd.read_excel(CITIES_FILE)
   
        match = df[df['city'].str.lower() == city_name.lower()]
        if not match.empty:
            latitude = match.iloc[0]['lat']
            longitude = match.iloc[0]['lng']
            return latitude, longitude
    except Exception as e:
        print(f"Error reading coordinates: {e}")
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            coords = get_coordinates(city)
            if coords:
                latitude, longitude = coords
                params = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'current_weather': 'true'
                }
                response = requests.get(BASE_URL, params=params)
                if response.status_code == 200:
                    data = response.json()
                    current = data['current_weather']
                    weather_data = {
                        'city': city.capitalize(),
                        'temperature': current['temperature'],
                        'wind_speed': current['windspeed'],
                        'description': "Windy" if current['windspeed'] > 10 else "Mild",
                    }
                else:
                    weather_data = {'error': 'Weather data not available.'}
            else:
                weather_data = {'error': 'City not found.'}
    return render_template('index.html', weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
