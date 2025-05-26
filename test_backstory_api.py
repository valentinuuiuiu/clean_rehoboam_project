import requests
import json

# Test the backstory generation API
def test_backstory_generation():
    url = "http://localhost:5002/api/companions/backstory/generate"
    
    payload = {
        "character_name": "Luna",
        "character_traits": [
            {"name": "Curious", "description": "Always seeking new knowledge", "intensity": 0.8},
            {"name": "Compassionate", "description": "Deeply empathetic to others", "intensity": 0.7}
        ],
        "cultural_influences": ["Science Fiction", "Classical Literature"],
        "story_depth": 0.8,
        "key_events": ["Discovery of ancient technology", "First contact with an alien civilization"]
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            print("Success! Backstory was generated.")
            print("\nResponse:")
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"Failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error testing backstory API: {str(e)}")

# Test the get backstory API (will fail if no companion exists)
def test_get_backstory():
    url = "http://localhost:5002/api/companions/Luna/backstory"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print("\nGet Backstory Success!")
            print("\nResponse:")
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"\nGet Backstory Failed with status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error testing get backstory API: {str(e)}")

if __name__ == "__main__":
    test_backstory_generation()
    # Uncomment to test getting a backstory for a specific companion
    # test_get_backstory()