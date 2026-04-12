import sys
import os
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.core.engine import TotalBeautyGuardianEngine

def test_routine_consultation():
    print("[Test] Starting Routine Consultation Test...")
    
    # Initialize Engine
    engine = TotalBeautyGuardianEngine()
    
    # User Provided Sample Input
    sample_request = {
        "user_id": "2c2d6f78-1aa1-417e-87de-686bf955fd0c",
        "analysis_type": "routine_consultation",
        "routine": [
            {
                "id": 1, 
                "icon": "item", 
                "name": "리얼 히알루로닉 앰플", 
                "brand": "MEDIHEAL", 
                "ingredients": ["Hyaluronic Acid", "Panthenol"],
                "routine_time": "am"
            }
        ],
        "skin_context": {
            "scores": {
                "radiance": 59, 
                "vitality": 24, 
                "resilience": 34, 
                "total_health": 203, 
                "climate_adaptability": 69
            }, 
            "biometrics": {
                "ita": 32.5, 
                "skin_age": 48, 
                "skin_type": "수분 부족형 지성", 
                "pore_density": "중간-높음", 
                "melanin_index": 70.0, 
                "wrinkle_score": 60.0
            }
        }
    }
    
    print(f"[Request] Sending request for {sample_request['analysis_type']}...")
    
    # Perform Analysis
    result = engine.analyze_routine_consultation(
        routine=json.dumps(sample_request["routine"]),
        skin_context=json.dumps(sample_request["skin_context"]),
        location="Seoul, Korea",
        lang="ko-KR"
    )
    
    # Print Result
    print("\n" + "=" * 40)
    print("[Report] ANALYSIS RESULT")
    print("=" * 40)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 40 + "\n")
    
    # Validate Structure
    required_keys = ["compatibility_score", "consult", "final_action", "scores"]
    missing = [k for k in required_keys if k not in result]
    
    if not missing:
        print("[Success] All required keys are present.")
        
        # Check if values are dynamic (not just placeholders)
        consult = result.get("consult", {})
        if consult.get("summary") and "히알루론" in str(consult):
             print("[Success] Result appears to be dynamically analyzed based on input.")
    else:
        print(f"[Failure] Missing keys: {missing}")

if __name__ == "__main__":
    test_routine_consultation()
