import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.core.engine import TotalBeautyGuardianEngine

def test_vanity_v1_2():
    print("[Test] Starting Vanity Analysis v1.2 Test...")
    
    # Initialize Engine
    engine = TotalBeautyGuardianEngine()
    
    # Client Provided Sample Input (Same as before but with analysis_type="vanity")
    sample_request = {
      "user_id": "user_jaesu_2026",
      "analysis_type": "vanity",
      "lang": "ko-KR",
      "location": "Seoul, Korea",
      "weather": "Sunny, Humidity 42%",
      "registration_data": {
        "age": 35,
        "gender": "male",
        "skin_type": "Combination",
        "skin_concerns": ["pores", "elasticity"],
        "fitzpatrick": 3
      },
      "skin_context": {
        "mode": "baseline_comparison",
        "baseline_id": "UUID-BASE-1234",
        "baseline_date": "2026-04-01",
        "previous_advice": "T존 유분 관리를 위해 일 2회 세안을 유지하고, 리들샷 사용 후 반드시 재생 크림을 두껍게 바르세요.",
        "scores": {
          "total_health": 71,
          "radiance": 62,
          "vitality": 55,
          "resilience": 59
        },
        "lifestyle": {
          "sleep_hours": 7.5,
          "water_intake_ml": 1800,
          "stress_level": "Low"
        }
      },
      "routine": [
        "VT 리들샷 100",
        "에스트라 아토베리어 365 크림",
        "헤라 UV 프로텍터"
      ],
      "camera": {
        "luminance": 120,
        "color_temp": 5500,
        "iso": 400
      }
    }
    
    # Perform Analysis
    # analyze_vanity is used for 'vanity' to get the raw JSON in v1.2.0-VANITY-PRO format
    result = engine.analyze_vanity(
        image_path=None, 
        location=sample_request["location"],
        registration_data=sample_request["registration_data"],
        weather_context=sample_request["weather"],
        lifestyle_24h="Balanced",
        camera_metadata=sample_request["camera"],
        current_routine=sample_request["routine"],
        lang=sample_request["lang"]
    )
    
    # Since analyze_image returns a TotalBeautyGuardianReport object for general, 
    # but for specialized types it might return a dict depending on how it's handled.
    # Actually, in engine.py line 213, it returns a report object for general.
    # Wait, for vanity, does it return a report or a dict?
    # Line 203 in engine.py: report = TotalBeautyGuardianReport(...)
    # It seems for 'vanity', it currently still builds a TotalBeautyGuardianReport.
    # BUT, the user wants a specific JSON format.
    
    print("\n" + "=" * 40)
    print("[Report] VANITY ANALYSIS RESULT (v1.2.0)")
    print("=" * 40)
    if hasattr(result, 'to_json'):
        print(result.to_json())
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 40 + "\n")

if __name__ == "__main__":
    test_vanity_v1_2()
