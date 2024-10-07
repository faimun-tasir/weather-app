from flask import Flask, render_template, request
import requests
from gtts import gTTS
import os

app = Flask(__name__)

def text_to_speech(weather_info):
    tts = gTTS(text=weather_info, lang='en')
    audio_file = 'static/weather.mp3'  
    tts.save(audio_file)
    return audio_file 

def get_lat_lon(city, state, country, api_key):
    complete_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{state},{country}&limit=1&appid={api_key}"
    
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        data = response.json()
        
        if data:
            lat = data[0]["lat"]
            lon = data[0]["lon"]
            return lat, lon
        else:
            return None, None

    except Exception as e:
        return None, None

def get_weather(city, lat, lon, api_key):
    complete_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(complete_url)
        response.raise_for_status()
        weather_data = response.json()

        if weather_data["cod"] != 200:
            return "Error fetching weather data."
        
        main = weather_data["main"]
        weather = weather_data["weather"][0]

        temperature = main["temp"]
        pressure = main["pressure"]
        humidity = main["humidity"]
        weather_description = weather["description"]

        weather_info = (f"Weather for {city.capitalize()}:\n"
                        f"Temperature: {temperature}°C\n"
                        f"Atmospheric pressure: {pressure} hPa\n"
                        f"Humidity: {humidity}%\n"
                        f"Weather description: {weather_description.capitalize()}")

        return weather_info
    
    except Exception as e:
        return str(e)

@app.route("/", methods=["GET", "POST"])
def index():
    weather_info = ""
    audio_file = "" 
    if request.method == "POST":
        city = request.form["city"]
        state = request.form["state"]
        country = request.form["country"]
        
        api_key = "218aa9860a4f0b8ba07d3e35e90b6bb8"  
        lat, lon = get_lat_lon(city, state, country, api_key)
        
        if lat is not None and lon is not None:
            weather_info = get_weather(city, lat, lon, api_key)
            audio_file = text_to_speech(weather_info)  

    return render_template("index.html", weather_info=weather_info, audio_file=audio_file)

if __name__ == "__main__":
    app.run(debug=True)
