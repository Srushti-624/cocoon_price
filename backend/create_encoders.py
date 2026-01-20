
import joblib
import os
from sklearn.preprocessing import LabelEncoder

def setup_encoders():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. City Encoder
    # Mappings MUST match the alphabetical order of the training data cities
    # Training Data (Notebook): Bengaluru, Ramanagar, Siddlaghatta
    # Frontend Options: Bengaluru, Ramanagara, Shidlaghatta
    # We map Frontend -> Integers
    # Ideally, we should train the encoder on the values we expect to RECEIVE from frontend
    # AND ensure those integers match what the model expects.
    # Model Expects: 0 (Ben), 1 (Ram), 2 (Sid)
    
    cities = ["Bengaluru", "Ramanagara", "Shidlaghatta"] 
    # Sorted: Bengaluru, Ramanagara, Shidlaghatta -> 0, 1, 2
    # This matches.
    
    le_city = LabelEncoder()
    le_city.fit(cities)
    joblib.dump(le_city, os.path.join(base_dir, "le_city.joblib"))
    print("City encoder created.")

    # 2. Season Encoder
    # Notebook: Summer, Monsoon, PostMonsoon, Winter
    # Sorted: Monsoon (0), PostMonsoon (1), Summer (2), Winter (3)
    seasons = ["Monsoon", "PostMonsoon", "Summer", "Winter"]
    
    le_season = LabelEncoder()
    le_season.fit(seasons)
    joblib.dump(le_season, os.path.join(base_dir, "le_season.joblib"))
    print("Season encoder created.")

if __name__ == "__main__":
    setup_encoders()
