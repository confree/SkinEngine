import json
import os

class SkinFoodCrossAnalyzer:
    """
    [VeriSkin-Cross-Analyzer-v1.0]
    Calculates Suitability Score by matching food nutrition with skin biometrics.
    """
    
    def __init__(self, logic_path: str):
        with open(logic_path, 'r', encoding='utf-8') as f:
            self.logic = json.load(f)
        
        self.k_food_risk = self.logic.get('k_food_specialized_risk', {})
        self.skin_sensitivity = {
            "Oily": 1.4,
            "Combination": 1.2,
            "Normal": 1.0,
            "Dry": 0.8
        }

    def calculate_suitability(self, food_data, biometrics):
        """
        Computes the 'Skin Suitability Score' (0-100) and provides clinical advice.
        """
        score = 100
        skin_type = biometrics.get("skin_type", "Normal")
        multiplier = self.skin_sensitivity.get(skin_type, 1.0)
        
        # 1. Specialized K-Food Check
        item_id = food_data.get("identified_item", "").lower()
        if item_id in self.k_food_risk:
            k_risk = self.k_food_risk[item_id]
            # Significant deduction for K-Food risk factor
            deduction = (k_risk.get("glycemic_impact", 0) + k_risk.get("fat_impact", 0)) * 40
            score -= deduction * multiplier
            prediction = k_risk.get("prediction", "데이터 부족")
        else:
            # 2. General Nutrient-based Deduction
            nutrients = food_data.get("nutrients", {})
            sugar = nutrients.get("sugar_g", 0) or 0
            fat = nutrients.get("fat_g", 0) or 0
            
            # Weighted deduction: Sugar(High GL) impacts oily skin more
            deduction = (sugar * 1.5 + fat * 1.2) * multiplier
            score -= deduction
            prediction = "식후 유수분 밸런스 변화 예의 주시 필요"

        final_score = max(0, min(100, round(score, 1)))
        
        # 3. Real-time Response (3-Line Summary)
        summary = self._generate_summary(final_score, prediction, skin_type)
        
        return {
            "suitability_score": final_score,
            "prediction": prediction,
            "summary_3_lines": summary,
            "alert_level": "Caution" if final_score < 50 else "Safe"
        }

    def _generate_summary(self, score, prediction, skin_type):
        """Generates clinical summary in 3 distinct lines."""
        line1 = f"[{skin_type} 피부 대조] 이 음식 영양 성분은 현재 고객님의 피부 밸런스와 {int(score)}%의 적합도를 보입니다."
        line2 = f"[예상 변화] {prediction}로 인해 피부 기상도 지수가 일시적으로 하락할 우려가 있습니다."
        line3 = "[케어 추천] 오늘 저녁은 약산성 클렌저로 T존을 꼼꼼히 세정하는 '집중 진정 관리'를 추천합니다."
        return [line1, line2, line3]

if __name__ == "__main__":
    # Internal test stub
    print("🚀 Skin-Food Cross Analyzer Logic Initialized.")
