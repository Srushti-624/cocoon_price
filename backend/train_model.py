
import pandas as pd
import numpy as np
from datetime import timedelta
import os
import joblib
from xgboost import XGBRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# --- Helper Functions ---
def get_season(m):
    if m in [3,4,5]: return "Summer"
    if m in [6,7,8,9]: return "Monsoon"
    if m in [10,11]: return "PostMonsoon"
    return "Winter"

def load_weather(file_path, city_name):
    print(f"Loading weather for {city_name} from {file_path}...")
    df = pd.read_csv(file_path)
    if "DOY" in df.columns:
        # Convert YEAR and DOY to proper Date
        df["date"] = pd.to_datetime(df["YEAR"], format="%Y") + pd.to_timedelta(df["DOY"]-1, unit="D")
    elif "DATE" in df.columns:
        df["date"] = pd.to_datetime(df["DATE"])
    else:
        raise ValueError(f"Could not parse date in {file_path}")
        
    df["city"] = city_name
    return df[["date","T2M","RH2M","PRECTOTCORR","city"]]

# --- Main Training Logic ---
def train():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Load Market Price (CRITICAL dependency)
    market_price_path = os.path.join(base_dir, "market_price.csv")
    if not os.path.exists(market_price_path):
        print("ERROR: market_price.csv not found in backend directory!")
        print("Please upload market_price.csv with columns: year, month, avg_price")
        # creating a dummy file for testing purposes if not found, to allow flow to continue (optional)
        # For now, we will raise error to alert user
        raise FileNotFoundError("market_price.csv is missing")

    market = pd.read_csv(market_price_path)
    # Ensure columns match expectations
    market.columns = [c.lower() for c in market.columns] # Handle Case sensitivity
    if "avg_price" not in market.columns and "price" in market.columns:
        market.rename(columns={"price": "avg_price"}, inplace=True)
    
    # 2. Load Weather Data
    weather_files = {
        "Bengaluru": "bengaluru_weather_data.csv",
        "Ramanagara": "ramanagar_weather_data.csv", # Note: Ramanagara vs ramanagar
        "Shidlaghatta": "siddlaghatta_weather_data.csv" # Note: Shidlaghatta vs siddlaghatta
    }
    
    dfs = []
    for city, filename in weather_files.items():
        path = os.path.join(base_dir, filename)
        if os.path.exists(path):
            dfs.append(load_weather(path, city))
        else:
            print(f"WARNING: Weather file {filename} not found.")
            
    if not dfs:
        raise FileNotFoundError("No weather data files found.")
        
    weather = pd.concat(dfs, ignore_index=True)
    
    # 3. Create Dataset (Samples)
    print("Creating training samples...")
    samples = []
    
    # Pre-filter market price for speed
    # We need to lookup price by (year, month)
    market_lookup = market.set_index(["year", "month"])["avg_price"].to_dict()

    for city in weather["city"].unique():
        w = weather[weather["city"]==city].sort_values("date")
        
        # Optimize: Iterate through dates efficiently
        # Doing it loop-wise as in notebook for fidelity, but it's slow.
        # Given dataset size (~4000 rows), it's acceptable.
        
        for i in range(len(w) - 25):
            start_row = w.iloc[i]
            start_date = start_row["date"]
            end_date = start_date + timedelta(days=24)
            
            # Using slice is faster than boolean indexing repeated
            # But the notebook did boolean. Let's trust pandas indexing.
            # We need a 25 day window.
            # Actually, `win = w[(w["date"]>=start)&(w["date"]<=end)]`
            
            # Fast filter:
            win = w.iloc[i : i+25]
            # Verify date range
            if (win.iloc[-1]["date"] - start_date).days > 25:
                # If gaps exist, filter strictly
                win = w[(w["date"]>=start_date)&(w["date"]<=end_date)]
                
            if len(win) < 25: continue
            
            harvest = end_date
            price = market_lookup.get((harvest.year, harvest.month))
            
            if price is None: continue
            
            samples.append({
                "city": city,
                "season": get_season(start_date.month),
                "avg_temp": win["T2M"].mean(),
                "max_temp": win["T2M"].max(),
                "avg_humidity": win["RH2M"].mean(),
                "rainfall": win["PRECTOTCORR"].sum(),
                "price": price
            })
            
    data = pd.DataFrame(samples)
    print(f"Dataset created with {len(data)} samples.")
    
    if data.empty:
        raise ValueError("No samples created. Check date overlap between weather and market price.")

    # 4. Encoders
    le_city = LabelEncoder()
    le_season = LabelEncoder()
    
    data["city_code"] = le_city.fit_transform(data["city"])
    data["season_code"] = le_season.fit_transform(data["season"])
    
    # Save Encoders
    joblib.dump(le_city, os.path.join(base_dir, "le_city.joblib"))
    joblib.dump(le_season, os.path.join(base_dir, "le_season.joblib"))
    
    # 5. Train Model
    X = data[["city_code", "season_code", "avg_temp", "max_temp", "avg_humidity", "rainfall"]]
    y = data["price"]
    
    print("Training XGBoost model...")
    model = XGBRegressor(
        n_estimators=600,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42
    )
    
    model.fit(X, y)
    
    # 6. Evaluate (Optional print)
    score = model.score(X, y)
    print(f"Model R2 Score on training data: {score}")
    
    # 7. Save Model
    joblib.dump(model, os.path.join(base_dir, "model.pkl"))
    print("Model saved to model.pkl")

if __name__ == "__main__":
    train()
