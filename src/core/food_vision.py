from google import genai
from google.genai import types
from PIL import Image
import json
import os
import re

class FoodVisionEngine:
    """
    [VeriSkin-Food-Vision-v1.0]
    Analyzes food labels (OCR) or dish photos (Recognition) to extract skin-impacting nutrients.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "AIzaSyD1MVFUZux4oHnk8hEimxgwFqKq7EaOENU"
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = 'models/gemini-2.0-flash'

    def analyze_food_image(self, image_path: str) -> dict:
        """
        Determines if the image is a Nutrition Label or a Dish, then extracts relevant metrics.
        """
        try:
            img = Image.open(image_path)
            
            prompt = (
                "Analyze this food image and return a JSON object with the following structure:\n"
                "{\n"
                "  \"image_type\": \"label\" or \"dish\",\n"
                "  \"identified_item\": \"string (e.g., Tteokbokki, Apple, etc.)\",\n"
                "  \"nutrients\": {\n"
                "    \"sugar_g\": float or null,\n"
                "    \"fat_g\": float or null,\n"
                "    \"sodium_mg\": float or null,\n"
                "    \"dairy\": boolean or null\n"
                "  },\n"
                "  \"confidence\": float (0.0 to 1.0)\n"
                "}\n"
                "If it's a label, use OCR to find exact values. If it's a dish, estimate based on standard Korean nutrition data."
            )
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, img]
            )
            
            if response and response.text:
                json_str = response.text.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                return {"error": "AI failed to analyze food image"}

        except Exception as e:
            print(f"⚠️ [Food-Vision] Error: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    # Internal test stub
    engine = FoodVisionEngine()
    print("🚀 Food Vision Engine Initialized.")
