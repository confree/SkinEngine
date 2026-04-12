import requests
import json

api_key = "AIzaSyD1MVFUZux4oHnk8hEimxgwFqKq7EaOENU"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    data = response.json()
    if "models" in data:
        print("Available Models:")
        for m in data["models"]:
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(f"- {m['name']}")
    else:
        print("Error/Response:", json.dumps(data, indent=2))
except Exception as e:
    print(f"Failed to fetch models: {e}")
