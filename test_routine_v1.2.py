import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.core.engine import TotalBeautyGuardianEngine

def test_routine_v1_2():
    print("[Test] Starting Routine Consultation v1.2 Test...")
    
    # Initialize Engine
    engine = TotalBeautyGuardianEngine()
    
    # Client Provided Sample Input
    sample_request = {
      "user_id": "user_jaesu_2026",
      "analysis_type": "routine_consultation",
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
    # Note: Since we don't have a real image path, it will use mock or skip image analysis
    result = engine.analyze_routine_consultation(
        routine=sample_request["routine"],
        skin_context=sample_request["skin_context"],
        location=sample_request["location"],
        registration_data=sample_request["registration_data"],
        weather_context=sample_request["weather"],
        camera_metadata=sample_request["camera"],
        lang=sample_request["lang"]
    )
    
    print("\n" + "=" * 40)
    print("[Report] ANALYSIS RESULT (v1.2.0)")
    print("=" * 40)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 40 + "\n")

if __name__ == "__main__":
    test_routine_v1_2()
