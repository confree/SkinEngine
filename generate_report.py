import requests
import json
import os

api_key = "AIzaSyD1MVFUZux4oHnk8hEimxgwFqKq7EaOENU"
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    data = response.json()
    with open("D:/Workspace/SkinEngine/model_list_report.txt", "w", encoding="utf-8") as f:
        if "models" in data:
            f.write("Available Generative Models:\n")
            for m in data["models"]:
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    f.write(f"- {m['name']}\n")
        else:
            f.write(f"Error in API: {json.dumps(data, indent=2)}")
    print("Report generated: model_list_report.txt")
except Exception as e:
    with open("D:/Workspace/SkinEngine/model_list_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Failed: {str(e)}")
