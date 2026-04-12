import json
import math
import os

class SkinRiskEngine:
    """
    [VeriSkin-Risk-Engine-v8.0]
    Calculates skin trouble probability based on clinical weights from skin_diet_logic_v1.json.
    """
    
    def __init__(self, logic_path: str):
        with open(logic_path, 'r', encoding='utf-8') as f:
            self.logic = json.load(f)
        
        self.weights = self.logic['scoring_logic']
        self.ethnicity_adj = self.logic['ethnicity_adjustment']

    def calculate_daily_skin_risk(self, food_items, ethnicity, weather_context, skin_type):
        """
        Calculates a trouble prediction score (0-100) and probability.
        """
        base_score = 15.0  # Base biological baseline
        
        # 1. Dietary Impact (GL & Fat)
        diet_score = 0
        if "Coke" in food_items or "High GL" in food_items:
            # GL Impact using OR 1.8 weighting
            diet_score += 25 * self.weights['glycemic_load']['impact_weight']
            
        if "Samgyeopsal" in food_items or "Fried Chicken" in food_items:
            # Fat Impact
            diet_score += 40 * self.weights['high_fat_intake']['impact_weight']

        # 2. Weather Impact (Sebum Secretion Rate increase)
        weather_score = 0
        if "Hot" in weather_context: weather_score += 12
        if "Humid" in weather_context: weather_score += 15
        
        # 3. Aggregation & Scaling
        raw_score = base_score + diet_score + weather_score
        
        # 4. Skin Type & Ethnicity Multipliers
        type_multiplier = 1.3 if skin_type.lower() == "oily" else 1.0
        ethnicity_multiplier = self.ethnicity_adj.get(ethnicity, 1.0)
        
        final_score = min(100, raw_score * type_multiplier * ethnicity_multiplier)
        
        # 5. Probability Modeling (Sigmoid transformation)
        # Probability that inflammatory acne triggers within 24h
        # Midpoint at 50, Steepness of 0.1
        probability = 1 / (1 + math.exp(-(final_score - 50) * 0.12))
        
        return {
            "skin_weather_score": round(final_score, 1),
            "trouble_sign_alert_24h": f"{round(probability * 100, 1)}%",
            "management_focus_factors": self._get_critical_factors(food_items, weather_context)
        }

    def _get_critical_factors(self, food, weather):
        factors = []
        if "Samgyeopsal" in food: factors.append("포화 지방 섭취로 인한 유수분 밸런스 영향")
        if "Coke" in food: factors.append("당부하 지수로 인한 과잉 피지 가능성")
        if "Humid" in weather: factors.append("고습도 환경에 따른 모공 폐쇄 주의")
        return factors

def match_shopify_products(risk_score):
    """Matches product IDs based on analysis score."""
    recommendations = []
    if risk_score >= 75:
        recommendations.append({
            "product_id": "PROD_001_OIL_FREE_SOOTHING",
            "line": "집중 진정 라인 (Oil-free)",
            "reason": "피부 기상도 지수 75점 초과 (집중 진정 관리 추천)"
        })
    return recommendations

if __name__ == "__main__":
    # Path setup
    KNOWLEDGE_PATH = "d:/Workspace/SkinEngine/knowledge/skin_diet_logic_v1.json"
    
    engine = SkinRiskEngine(KNOWLEDGE_PATH)
    
    # [Scenario] Korean Oily Skin, Samgyeopsal + Coke, Chiang Rai (Hot/Humid)
    result = engine.calculate_daily_skin_risk(
        food_items=["Samgyeopsal", "Coke"],
        ethnicity="korean_asian",
        weather_context="Hot, Humid (Chiang Rai)",
        skin_type="Oily"
    )
    
    products = match_shopify_products(result['skin_weather_score'])
    
    full_report = {
        "analysis_version": "v8.1-SafeGuard",
        "customer_profile": {
            "ethnicity": "Korean/Asian",
            "skin_type": "지성(Oily)",
            "current_location": "치앙라이 (태국)"
        },
        "daily_event": {
            "consumed": ["삼겹살", "콜라"],
            "environmental_status": "고온 다습"
        },
        "skin_weather_analysis": {
            "weather_score": result['skin_weather_score'],
            "trouble_sign_alert_24h": result['trouble_sign_alert_24h'],
            "management_focus_factors": result['management_focus_factors']
        },
        "care_recommendations": products,
        "executive_summary": "고객님의 현재 식단과 기후 환경이 지명 피부의 평상시 수준을 상회하고 있습니다. 당부하와 지방 섭취가 피부 유수분 밸런스에 영향을 줄 우려가 있으니, 24시간 내 집중 진정 관리를 통한 선제적 대응을 추천합니다."
    }
    
    print(json.dumps(full_report, indent=2, ensure_ascii=False))
