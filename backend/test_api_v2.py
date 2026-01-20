
import requests
import json
import sys

def test_recommend():
    url = "http://localhost:5000/recommend"
    payload = {"location": "Bengaluru"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Success!")
        print(f"Recommended Start: {data.get('recommended_date')}")
        print(f"Expected Harvest: {data.get('expected_harvest_date')}")
        print(f"Predicted Price: {data.get('predicted_price')}")
        
        # Check first prediction in list
        first_pred = data.get('all_predictions')[0]
        print(f"First Prediction Entry: {first_pred}")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'response' in locals():
            print("Status Code:", response.status_code)
            print("Response Content:", response.text)
        sys.exit(1)

if __name__ == "__main__":
    test_recommend()
