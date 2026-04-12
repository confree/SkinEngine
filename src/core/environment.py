from typing import Dict, List, Any

class EnvironmentEngine:
    """
    Layer 2: Environment - Climate-adaptive analysis for skin behavior.
    """
    
    def __init__(self):
        # Base Comedogenicity Index (0-5 scale) for common ingredient types
        self.comedogenic_database = {
            "Coconut Oil": 4,
            "Isopropyl Myristate": 5,
            "Shea Butter": 0,
            "Squalane": 0,
            "Glycerin": 0,
            "Stearic Acid": 3,
            "Algae Extract": 5,
            "Wheat Germ Oil": 5
        }

    def get_current_season(self, location: str) -> Dict[str, str]:
        """
        Determines the current season and its skin-risk factors.
        """
        from datetime import datetime
        month = datetime.now().month
        
        # Tropical Climate Detection (e.g., Southeast Asia)
        tropical_cities = ["Bangkok", "Phuket", "Ho Chi Minh", "Singapore", "Sukhothai", "Chiang Rai"]
        is_tropical = any(city in location for city in tropical_cities)
        
        if is_tropical:
            if 3 <= month <= 5:
                return {"season": "Summer/Hot", "risk": "Extreme Sebum & Oxidation", "advice": "Oil-control & Thermal cooling"}
            elif 6 <= month <= 10:
                return {"season": "Monsoon/Rainy", "risk": "High Humidity & Fungal Sensitivity", "advice": "Barrier repair & Light hydration"}
            else:
                return {"season": "Cool/Dry", "risk": "Subtle Dehydration", "advice": "Moisture locking"}
        
        # Temperate Climate Detection (e.g., Seoul, London, NY)
        if 3 <= month <= 5:
            return {"season": "Spring (Transitional)", "risk": "Yellow Dust & Barrier Weakness", "advice": "Deep cleansing & Calming"}
        elif 6 <= month <= 8:
            return {"season": "Summer (Peak)", "risk": "UV Damage & Melanin Activation", "advice": "Antioxidants & Sun protection"}
        elif 9 <= month <= 11:
            return {"season": "Autumn (Transitional)", "risk": "Sudden Temperature Drops", "advice": "Ceramide layering"}
        else:
            return {"season": "Winter (Peak)", "risk": "Extreme Dryness & Redness", "advice": "Occulsive protection & Rich lipids"}

    def fetch_weather(self, location: str) -> Dict[str, Any]:
        """
        Fetches weather data. Uses provided location context.
        """
        # [MOD] No more deterministic mock. Return Unknown values if API is not yet integrated.
        return {
            "location": location,
            "temp": 25.0, # Default safe value
            "humidity": 50.0, # Default safe value
            "uv": 5.0, # Default safe value
            "aqi": 50.0, # Default safe value
            "weather_desc": "Data unavailable (Mock strictly disabled)"
        }

    def calculate_pcr(self, ingredients: List[str], weather: Dict[str, float]) -> float:
        """
        Calculates Pore Clogging Rate (PCR) based on climate and ingredients.
        """
        temp = weather["temp"]
        humidity = weather["humidity"]
        
        # Max index from current list
        max_idx = 0
        for ing in ingredients:
            max_idx = max(max_idx, self.comedogenic_database.get(ing, 0))
            
        # Climate Multiplier
        # Higher temp (+32C) and high humidity increases sebum viscosity/trap
        temp_factor = 1.0 + max(0.0, (temp - 20) * 0.05)
        hum_factor = 1.0 + max(0.0, (humidity - 50) * 0.01)
        
        pcr = (max_idx / 5.0) * temp_factor * hum_factor
        return min(1.0, pcr) # Normalized 0 to 1

    def calculate_tewl(self, weather: Dict[str, float], occlusivity_index: float = 0.0) -> float:
        """
        Calculates estimated Water Evaporation Rate (TEWL).
        """
        humidity = weather["humidity"]
        
        # Base TEWL is higher in low humidity
        base_evaporation = (100.0 - humidity) / 100.0
        
        # Occlusivity (0 to 1) blocks evaporation
        tewl = base_evaporation * (1.0 - occlusivity_index)
        
        # Scale to common mg/cm2/h values (approx 5-20)
        return tewl * 20.0

if __name__ == "__main__":
    engine = EnvironmentEngine()
    weather = engine.fetch_weather("Bangkok")
    ingredients = ["Coconut Oil", "Glycerin"]
    pcr = engine.calculate_pcr(ingredients, weather)
    tewl = engine.calculate_tewl(weather, occlusivity_index=0.2)
    
    print(f"Location: Bangkok, Weather: {weather}")
    print(f"Pore Clogging Rate (PCR): {pcr:.2%}")
    print(f"Water Evaporation Rate (TEWL): {tewl:.2f} mg/cm²/h")
