import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.getcwd()))

from src.core.engine import TotalBeautyGuardianEngine

def test_smoothing():
    engine = TotalBeautyGuardianEngine()
    
    # Mock history: Moving up slowly
    history = [
        {"scores": {"total_health": 60, "radiance": 50, "vitality": 55, "resilience": 60, "climate_adaptability": 70}},
        {"scores": {"total_health": 62, "radiance": 52, "vitality": 57, "resilience": 62, "climate_adaptability": 72}}
    ]
    
    # 1. Test Small Variation (Within threshold 8)
    # Raw current: 65 -> Diff from avg(61) is 4. Final should be 61 + 4*0.3 = 62.2 -> 62
    smoothed = engine._apply_score_smoothing(65, [60, 62])
    print(f"Test 1 (Small Change): Raw=65, History=[60, 62], Smoothed={smoothed} (Expected: ~62)")
    
    # 2. Test Large Variation (Outside threshold 8)
    # Raw current: 80 -> Diff from avg(61) is 19. Final should be 61 + 19*0.7 = 74.3 -> 74
    smoothed_large = engine._apply_score_smoothing(80, [60, 62])
    print(f"Test 2 (Large Change): Raw=80, History=[60, 62], Smoothed={smoothed_large} (Expected: ~74)")

    # 3. Test No History
    no_hist = engine._apply_score_smoothing(65, [])
    print(f"Test 3 (No History): Raw=65, History=[], Smoothed={no_hist} (Expected: 65)")

if __name__ == "__main__":
    test_smoothing()
