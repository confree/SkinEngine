import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.getcwd()))

from src.core.engine import TotalBeautyGuardianEngine
from src.core.guardian_schema import ProfessionalBiometrics, FaceGeometry, PersonalColor

def verify_scores():
    engine = TotalBeautyGuardianEngine()
    
    # Mock Biometrics (New 0-100 scale)
    bio = ProfessionalBiometrics(
        skin_age=45,
        ita=38.5,
        skin_type="Normal",
        skin_hex="#b48e6c",
        elasticity_score=68.5, # 0-100
        melanin_index=55.2,
        erythema_index=12.8,
        pore_density="Normal",
        wrinkle_score=58.0,    # 0-100
        age_range="40s",
        confidence_score=90
    )
    
    face = FaceGeometry(shape="Oval", length_width_ratio=1.4, asymmetry="None", jaw_tension="Normal", styling_recommendations={})
    color = PersonalColor(cielab={"L": 65, "a": 10, "b": 22}, seasonal_type="Autumn", undertone="Warm", recommended_palette=[], eye_hair_match="")
    weather = {"humidity": 30, "uv": 5}
    
    scores = engine._calculate_skin_scores(bio, face, color, weather)
    
    print(f"--- Score Verification ---")
    print(f"Elasticity: {bio.elasticity_score}")
    print(f"ITA: {bio.ita}")
    print(f"Wrinkle: {bio.wrinkle_score}")
    print(f"--------------------------")
    print(f"Total Health: {scores.total_health}")
    print(f"Radiance: {scores.radiance}")
    print(f"Vitality: {scores.vitality}")
    print(f"Resilience: {scores.resilience}")
    
    # Expected Total Health calculation:
    # e_comp = 68.5
    # t_comp = (38.5 / 55.0) * 100 = 70.0
    # w_comp = 100 - 58.0 = 42.0
    # total = 68.5 * 0.3 + 70.0 * 0.4 + 42.0 * 0.3
    # total = 20.55 + 28.0 + 12.6 = 61.15 -> 61
    
    if 60 <= scores.total_health <= 62:
        print("\n✅ Verification SUCCESS: Total Health is in realistic range (61)")
    else:
        print(f"\n❌ Verification FAILED: Total Health is {scores.total_health}")

if __name__ == "__main__":
    verify_scores()
