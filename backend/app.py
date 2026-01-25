from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv() # Load variables from .env if present

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Configuration ---
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Global variables
model = None
le_city = None
le_season = None
weather_data = None

def get_season(m):
    if m in [3,4,5]: return "Summer"
    if m in [6,7,8,9]: return "Monsoon"
    if m in [10,11]: return "PostMonsoon"
    return "Winter"

def load_weather(file_path, city_name):
    df = pd.read_csv(file_path)
    if "DOY" in df.columns:
        df["date"] = pd.to_datetime(df["YEAR"], format="%Y") + pd.to_timedelta(df["DOY"]-1, unit="D")
    elif "DATE" in df.columns:
        df["date"] = pd.to_datetime(df["DATE"])
    else:
        pass 
    df["city"] = city_name
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    return df[["date","month", "day", "T2M","RH2M","PRECTOTCORR","city"]]

def init_app():
    global model, le_city, le_season, weather_data
    
    # Load Model & Encoders
    try:
        model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
        le_city = joblib.load(os.path.join(BASE_DIR, "le_city.joblib"))
        le_season = joblib.load(os.path.join(BASE_DIR, "le_season.joblib"))
        print("Model and encoders loaded successfully.")
    except Exception as e:
        print(f"Error loading model/encoders: {e}")
        
    # Load Weather for historical averages
    dfs = []
    weather_files = {
        "Bengaluru": "bengaluru_weather_data.csv",
        "Ramanagara": "ramanagar_weather_data.csv",
        "Siddlaghatta": "siddlaghatta_weather_data.csv"
    }
    for city, filename in weather_files.items():
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            dfs.append(load_weather(path, city))
    
    if dfs:
        weather_data = pd.concat(dfs, ignore_index=True)
        print("Weather data loaded for historical averages.")
    else:
        print("Warning: No weather data found.")

def get_historical_weather(city, start_date, days=25):
    target_date_range = [start_date + timedelta(days=i) for i in range(days)]
    
    temps = []
    humidities = []
    rainfalls = []
    
    city_df = weather_data[weather_data["city"] == city]
    if city_df.empty:
        return None
        
    for d in target_date_range:
        matches = city_df[(city_df["month"] == d.month) & (city_df["day"] == d.day)]
        if not matches.empty:
            temps.append(matches["T2M"].mean())
            humidities.append(matches["RH2M"].mean())
            rainfalls.append(matches["PRECTOTCORR"].mean())
            
    if not temps: return None
    
    return {
        "avg_temp": np.mean(temps),
        "max_temp": np.max(temps), 
        "avg_humidity": np.mean(humidities),
        "rainfall": np.sum(rainfalls)
    }

# --- Auth Endpoints ---

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
        
    # Check if user exists
    if mongo.db.users.find_one({"username": username}):
        return jsonify({"error": "Username already exists"}), 400
        
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    mongo.db.users.insert_one({
        "username": username,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    })
    
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = mongo.db.users.find_one({"username": username})
    
    if user and bcrypt.check_password_hash(user["password"], password):
        # Convert ObjectId to string for JWT identity
        access_token = create_access_token(identity=str(user["_id"]))
        return jsonify({"token": access_token, "username": username}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/history', methods=['GET'])
@jwt_required()
def history():
    current_user_id = get_jwt_identity()
    
    # Query using string ID (assuming we store user_id as string in recommendations)
    # OR convert to ObjectId if we stored it as ObjectId. 
    # Let's store as string to be safe and consistent with JWT.
    
    history_cursor = mongo.db.recommendations.find({"user_id": current_user_id}).sort("created_at", -1)
    
    data = []
    for item in history_cursor:
        data.append({
            "id": str(item["_id"]),
            "location": item["location"],
            "start_date": item["start_date"],
            "harvest_date": item["harvest_date"],
            "predicted_price": item["predicted_price"],
            "created_at": item["created_at"].strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(data)

@app.route('/recommend', methods=['POST'])
def recommend():
    if not model:
        return jsonify({"error": "Model not loaded. Please train model first."}), 500
        
    data = request.json
    location = data.get('location')
    
    if location not in ["Bengaluru", "Ramanagara", "Shidlaghatta", "Siddlaghatta"]:
        return jsonify({"error": "Invalid location"}), 400
        
    results = []
    today = datetime.now().date()
    
    for i in range(1, 11):
        start_date = today + timedelta(days=i)
        weather_stats = get_historical_weather(location, start_date)
        if not weather_stats:
            continue
            
        try:
            # Model expects 'Ramanagar' instead of 'Ramanagara'
            model_location = location
            if location == "Ramanagara":
                model_location = "Ramanagar"
            
            city_code = le_city.transform([model_location])[0]
            season_str = get_season(start_date.month)
            season_code = le_season.transform([season_str])[0]
        except Exception as e:
            return jsonify({"error": f"Encoding error: {str(e)}"}), 500
            
        harvest_date = start_date + timedelta(days=25) # Updated to 25 days cycle
        
        # DEBUG: print(f"Features: City={location}, Month={harvest_date.month} (Harvest), Season={season_str}")

        # Fix: Model expects 'city', 'month', 'season' features
        # CRITICAL FIX: Colab uses 'harvest_month' (end_date.month) for the 'month' feature!
        features = pd.DataFrame([{
            "city": city_code,   
            "month": harvest_date.month, # Matches Colab logic (Harvest Month)
            "season": season_code, 
            "avg_temp": weather_stats["avg_temp"],
            "max_temp": weather_stats["max_temp"],
            "avg_humidity": weather_stats["avg_humidity"],
            "rainfall": weather_stats["rainfall"]
        }])
        
        # Ensure correct column order: city, month, season, ...
        features = features[["city", "month", "season", "avg_temp", "max_temp", "avg_humidity", "rainfall"]]
        
        print(f"DEBUG PREDICTING FOR {location} on {start_date}:")
        print(features.to_string())
        
        predicted_price = model.predict(features)[0]
        
        results.append({
            "start_date": start_date.strftime("%Y-%m-%d"),
            "harvest_date": harvest_date.strftime("%Y-%m-%d"),
            "predicted_price": float(predicted_price)
        })
        
    results.sort(key=lambda x: x["predicted_price"], reverse=True)
    best_rec = results[0]
    
    # Save to History if Logged In
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            mongo.db.recommendations.insert_one({
                "user_id": user_id, # Storing as string matches JWT identity
                "location": location,
                "start_date": best_rec["start_date"],
                "harvest_date": best_rec["harvest_date"],
                "predicted_price": best_rec["predicted_price"],
                "created_at": datetime.utcnow()
            })
    except Exception as e:
        print(f"History save error: {e}")
        pass
    
    return jsonify({
        "recommended_date": best_rec["start_date"],
        "expected_harvest_date": best_rec["harvest_date"],
        "predicted_price": best_rec["predicted_price"],
        "all_predictions": results
    })

if __name__ == '__main__':
    init_app()
    app.run(debug=True, port=5000)
