from google import genai
from google.genai import types
import os
import json
import base64
import datetime
from pathlib import Path
from typing import Dict, Any

class GeminiVisionEngine:
    """
    Phase 5: Gemini 1.5 Vision Integration - Migrated to google.genai v2.2
    [MOCK MODE DISABLED BY POLICY]
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "AIzaSyDqC9Rp3Dba7XICdE8dnOmhqJvqDWA36V8"
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-1.5-flash"
        
        self.system_instruction = (
            "You are a world-class dermatological AI. Analyze the facial image and return ONLY strict JSON."
        )

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Performs AI vision analysis without fallbacks."""
        if not self.api_key:
             raise RuntimeError("Legacy API Key missing. Mock mode is DISABLED.")
        
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    self.system_instruction,
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                ]
            )
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini")

            json_str = response.text.strip().replace("```json", "").replace("```", "")
            result = json.loads(json_str)
            self._save_to_logs(result)
            return result
            
        except Exception as e:
            print(f"❌ [Legacy-Vision] Analysis failed: {e}")
            raise e

    def _save_to_logs(self, data: Dict[str, Any]):
        try:
            log_dir = Path("logs/analysis_results")
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"result_{timestamp}.json"
            filepath = log_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[SUCCESS] Analysis result saved to: {filepath}")
        except Exception as e:
            print(f"[FAILURE] Failed to save log: {e}")

if __name__ == "__main__":
    print("[Legacy-Vision] GeminiVisionEngine Loaded. (Mock mode: DISABLED)")
