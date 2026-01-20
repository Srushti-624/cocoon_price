
import requests
import json
import sys

def test_recommend():
    url = "http://localhost:5000/recommend"
    payload = {"location": "Ramanagara"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Success!")
        print(f"Recommended Date: {data.get('recommended_date')}")
        print(f"Predicted Price: {data.get('predicted_price')}")
        # print("Response:", json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        if 'response' in locals():
            print("Status Code:", response.status_code)
            print("Response Content:", response.text)
        sys.exit(1)

if __name__ == "__main__":
    test_recommend()
