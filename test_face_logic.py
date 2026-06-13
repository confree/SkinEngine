import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from src.core.engine import TotalBeautyGuardianEngine

def test_face_analysis():
    print("🚀 [TEST] Face Analysis v3.1.7-PRO Verification")
    engine = TotalBeautyGuardianEngine(api_key="MOCK_KEY")
    
    # Simulate face analysis
    report = engine.analyze_image(
        image_path="dummy_face.jpg",
        location="Seoul",
        registration_data={"age": 28, "sex": "Female", "race": "Asian"},
        weather_context="Clear, Humidity: 45%",
        lifestyle_24h="Good sleep",
        camera_metadata={"luminance": 120},
        current_routine=["Water Cream"]
    )
    
    report_json = json.loads(report.to_json())
    
    print(f"✅ Version: {report_json.get('version')}")
    print(f"✅ Image Type: {report_json.get('image_type')}")
    
    # Check for all 8 major sections
    sections = ["biometrics", "face", "color", "curation", "consult", "risks", "dossier", "final_action"]
    for s in sections:
        status = "FOUND" if s in report_json else "MISSING"
        print(f"🔍 Section [{s}]: {status}")
        
    # Check Final Action details
    fa = report_json.get("final_action", {})
    print(f"💡 Final Action Risk: {fa.get('risk_summary')}")
    print(f"💡 Final Action Tip: {fa.get('professional_tip')}")
    print(f"💡 Final Action Routine: {fa.get('offset_routine')}")
    
    print("-" * 50)

def test_clinical_translation():
    print("\n🚀 [TEST] Clinical Ground Truth Translation & Injection Verification")
    engine = TotalBeautyGuardianEngine()
    
    from src.core.guardian_schema import ProfessionalBiometrics, FaceGeometry, PersonalColor
    
    bio = ProfessionalBiometrics(
        skin_age=28,
        ita=45.0,
        skin_type="Dry",
        skin_hex="#FFFFFF",
        elasticity_score=75.0,
        melanin_index=30.0,
        erythema_index=15.0,
        pore_density="Normal",
        wrinkle_score=20.0,
        age_range="20s",
        confidence_score=90
    )
    face = FaceGeometry(shape="Oval", length_width_ratio=1.4, asymmetry="None", jaw_tension="Normal", styling_recommendations={})
    color = PersonalColor(cielab={"L": 65, "a": 10, "b": 20}, seasonal_type="Spring", undertone="Warm", recommended_palette=[], eye_hair_match="Good")
    weather = {"location": "Seoul", "humidity": 45, "weather_desc": "Clear", "season_info": {"season": "Spring", "risk": "Low", "advice": "Hydrate"}}
    
    # 1. 한국어 검증 (lang="ko")
    ai_consult_ko = {
        "summary": "종합 분석 요약입니다.",
        "skincare": "스킨케어 가이드",
        "makeup": "메이크업 가이드",
        "hair": "헤어 가이드",
        "detected_keywords": ["여드름"]
    }
    
    print("\n--- Testing lang='ko' ---")
    consult_ko = engine._generate_expert_consult(bio, face, color, weather, ai_consult_ko, lang="ko")
    print(f"Summary (KO):\n{consult_ko.summary}")
    
    # 2. 영어 번역 검증 (lang="en")
    ai_consult_en = {
        "summary": "Comprehensive analysis summary.",
        "skincare": "Skincare guide",
        "makeup": "Makeup guide",
        "hair": "Hair guide",
        "detected_keywords": ["Acne"]
    }
    
    print("\n--- Testing lang='en' ---")
    consult_en = engine._generate_expert_consult(bio, face, color, weather, ai_consult_en, lang="en")
    print(f"Summary (EN):\n{consult_en.summary}")

def test_face_analysis_real():
    print("🚀 [TEST] Face Analysis v3.1.7-PRO Verification")
    engine = TotalBeautyGuardianEngine() # Use .env key
    
    report = engine.analyze_image(
        image_path="dummy.jpg",
        location="Seoul",
        registration_data={"age": 28, "sex": "Female", "race": "Asian"},
        weather_context="Clear, Humidity: 45%",
        lifestyle_24h="I suffer from severe acne vulgaris breakout and rosacea redness on my face.",
        camera_metadata={"luminance": 120},
        current_routine=["Water Cream"]
    )
    
    report_json = json.loads(report.to_json())
    print(f"✅ Version: {report_json.get('version')}")
    print(f"✅ Image Type: {report_json.get('image_type')}")
    
    sections = ["biometrics", "face", "color", "curation", "consult", "risks", "dossier", "final_action"]
    for s in sections:
        status = "FOUND" if s in report_json else "MISSING"
        print(f"🔍 Section [{s}]: {status}")

if __name__ == "__main__":
    # Use existing dummy image
    img_path = "dummy.jpg"
    if not os.path.exists(img_path):
        from PIL import Image
        img = Image.new('RGB', (100, 100), color = 'white')
        img.save(img_path)
    
    try:
        test_face_analysis_real()
        test_clinical_translation()
    except Exception as e:
        print(f"❌ Test Failed: {e}")

