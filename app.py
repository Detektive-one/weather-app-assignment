from flask import Flask, render_template, request
import pandas as pd
import requests
import os

app = Flask(__name__, static_folder='static')
CITIES_FILE = os.path.join(app.static_folder, 'worldcities.xlsx')

def get_coordinates(city_name):
    data = pd.read_excel(CITIES_FILE)
    city = data[data['city_ascii'].str.lower() == city_name.lower()]
    if not city.empty:
        latitude = city.iloc[0]['lat']
        longitude = city.iloc[0]['lng']
        return latitude, longitude
    return None, None

def fetch_weather_data(latitude, longitude, params, data_type):
    if data_type == 'current':
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly={','.join(params)}"
    elif data_type == 'historical':
        url = f"https://archive-api.open-meteo.com/v1/era5?latitude={latitude}&longitude={longitude}&start_date=2021-01-01&end_date=2021-12-31&hourly={','.join(params)}"

    response = requests.get(url)
    if response.status_code == 200:
        hourly_data = response.json().get('hourly', {})
        
        formatted_data = []
        for i, timestamp in enumerate(hourly_data.get('time', [])):
            hour_info = {'time': timestamp}
            for param in params:
                hour_info[param] = hourly_data.get(param, [None])[i]
            formatted_data.append(hour_info)
        return formatted_data
    
    return []

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = {}
    city = None

    if request.method == 'POST':
        city = request.form['city']
        parameters = request.form.getlist('parameters')
        data_type = request.form['data_type']

        latitude, longitude = get_coordinates(city)
        if latitude and longitude:
            weather_data = fetch_weather_data(latitude, longitude, parameters, data_type)
        else:
            weather_data = {'Error': 'City not found in the database'}

    return render_template('index.html', weather_data=weather_data, city=city)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
