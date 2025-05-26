import requests
import json
import time
import os

# Set the test mode environment variable - this would be set in a real environment
# We're setting it in the test script to ensure fast test execution
os.environ["REHOBOAM_TEST_MODE"] = "true"

# API endpoint
url = "http://localhost:5002/api/companions/backstory/generate"

# Test payload
payload = {
    "character_name": "Luna",
    "character_traits": [
        {"name": "Curious", "description": "Always seeking new knowledge", "intensity": 0.8}
    ],
    "cultural_influences": ["Science Fiction"],
    "story_depth": 0.5
}

# Make the request with a longer timeout (60 seconds)
try:
    print("Sending request to generate backstory for Luna...")
    print("Using REHOBOAM_TEST_MODE=true for fast testing...")
    start_time = time.time()
    
    response = requests.post(url, json=payload, timeout=60)
    
    elapsed_time = time.time() - start_time
    print(f"Request completed in {elapsed_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("\nBackstory generation successful!")
        result = response.json()
        
        # Print a summary of the result
        print("\nResponse content summary:")
        print(f"- Backstory length: {len(result.get('backstory', ''))} characters")
        print(f"- Key moments: {len(result.get('key_moments', []))} items")
        print(f"- Relationships: {len(result.get('relationships', []))} items")
        print(f"- Secrets: {len(result.get('secrets', []))} items")
        print(f"- Future goals: {len(result.get('future_goals', []))} items")
        
        # Print the first 200 characters of the backstory
        backstory = result.get('backstory', '')
        if backstory:
            print("\nBackstory excerpt:")
            print(backstory[:200] + "..." if len(backstory) > 200 else backstory)
    else:
        print("Failed to generate backstory")
        print(response.text)
except Exception as e:
    print(f"Error: {e}")