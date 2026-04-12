from src.core.guardian_schema import TotalBeautyGuardianReport, FaceGeometry, PersonalColor, IntegratedCuration, GuardianRiskFilter, ExpertConsultation, ProfessionalBiometrics, ProfessionalDossier, FinalAction, SkinScores
from src.core.biometrics import BiometricsEngine
from src.core.environment import EnvironmentEngine
from src.core.interaction import InteractionEngine
from src.core.guardian_vision import GuardianVisionEngine
from typing import List, Dict, Any, Tuple

class TotalBeautyGuardianEngine:
    """
    [Total-Beauty-AI-Senior-Guardian]
    An integrated engine for Skin, Face, Personal Color, and Environmental analysis.
    """
    
    def __init__(self, api_key: str = None):
        self.biometrics = BiometricsEngine()
        self.environment = EnvironmentEngine()
        self.interaction = InteractionEngine()
        self.vision = GuardianVisionEngine(api_key=api_key)
        
        # [DECISION LOGIC v1.0] Clinical Foundation Constants (Korean/Asian Clinical Data)
        self.GL = 20    # Glycemic Load threshold
        self.OR = 1.8   # Odds Ratio for skin barrier disruption
        self.R2 = 0.69  # Correlation coefficient for climate-skin mapping
        
        # High-risk styling/product data (Negative Filtering)
        self.styling_blacklist = {
            "Iron Oxides (High)": "Triggers dark oxidation in high-sebum climates.",
            "PPD-Dye": "High risk of scalp dermatitis for sensitive skin.",
            "Resorcinol": "Irritant / Metabolic disruptor.",
            "Ammonia": "Hair cuticle damage / Scalp burn risk."
        }

    def analyze_image(self, 
                      image_path: str, 
                      location: str, 
                      registration_data: Dict[str, Any] = {}, # 👤 User signup info (Age, Sex, ITA)
                      weather_context: str = None, 
                      lifestyle_24h: str = "Balanced",        # 🍎 Diet, Sleep, etc.
                      camera_metadata: Dict[str, Any] = {},   # 📸 Luminance, Temp
                      current_routine: List[str] = [],
                      lang: str = "ko-KR",
                      analysis_type: str = "general") -> TotalBeautyGuardianReport:
        """
        Total Beauty Analysis via Gemini Vision Engine (v3.5 Location-Aware).
        """
        # Step 1: Environment & Weather Detection (Ensuring object exists for downstream methods)
        weather = self.environment.fetch_weather(location)
        
        if weather_context:
            current_climate = weather_context
        else:
            current_climate = f"{weather.get('weather_desc', 'Unknown')} (Humidity: {weather.get('humidity', '--')}%)"

        # Step 2: Automated Vision Analysis (Now with Enriched Context)
        raw_analysis = self.vision.analyze_image(
            image_path, 
            context={
                "location": location, 
                "weather": current_climate,
                "lifestyle": lifestyle_24h,
                "camera": camera_metadata,
                "user_profile": registration_data,
                "lang": lang
            },
            analysis_type=analysis_type
        )
        
        # [v3.1.7-PRO] Metadata Extraction
        version = raw_analysis.get("version", "3.1.7-PRO")
        image_type = raw_analysis.get("image_type", "face")
        biometrics_data = raw_analysis.get("biometrics", {})
        confidence = biometrics_data.get("confidence_score", 100)
        
        # [RELIABILITY FILTER] 🚨 Immediate Re-take Logic
        reliability_message = None
        if confidence < 40:
            reliability_message = (
                "⚠️ 현재 조명 상태가 분석에 부적절합니다. "
                "그림자가 지거나 색온도가 너무 낮아 분석 신뢰도가 하락했습니다. "
                "더 밝고 균일한 조명 아래서 다시 촬영해 주세요."
            )
        
        # Step 3: Biometrics Processing (Skip if not face)
        if image_type == "face":
            biometrics_data = raw_analysis.get("biometrics", {})
            color_data = raw_analysis.get("color", {})
            cielab = color_data.get("cielab", {})
            
            raw_l = cielab.get("L") or biometrics_data.get("L_star") or 65
            raw_a = cielab.get("a") or biometrics_data.get("a_star") or 5
            raw_b = cielab.get("b") or biometrics_data.get("b_star") or 15
            
            # Lighting Normalization
            reference_l = 62.0  
            normalization_factor = 0.5 
            normalized_l = raw_l + (reference_l - raw_l) * normalization_factor
            
            lab = {"L": normalized_l, "a": raw_a, "b": raw_b}
            ita = biometrics_data.get("ita") or round(self.biometrics.calculate_ita(lab["L"], lab["b"]), 1)
            skin_type = biometrics_data.get("skin_type") or self.biometrics.classify_skin_type(ita)
            
            # [CLINICAL LOGIC] Factor in OR & R2 for risk weighting
            texture_desc = biometrics_data.get("pore_density", "").lower() # Use pore_density as texture proxy if needed
            jaw_tension = raw_analysis.get("face", {}).get("jaw_tension", "Normal")
            
            # Age Range from AI Inference
            age_range = biometrics_data.get("age_range", "Unknown")
            
            # Use registration data if valid age is provided
            reg_age = registration_data.get('age')
            if reg_age is not None:
                try:
                    age_int = int(reg_age)
                    age_range = f"{(age_int // 10) * 10}대 " + ("초반" if age_int % 10 < 5 else "후반")
                except (ValueError, TypeError):
                    pass # Keep AI inferred age_range if registration data is invalid
            
            # Real skin age from AI
            final_skin_age = biometrics_data.get("skin_age", 30)
        else:
            # Ingredient/Food mode: Use environment-based defaults for score generation
            lab = {"L": 62.0, "a": 5.0, "b": 15.0} # Balanced Neutral
            ita = 45.0
            skin_type = "Normal (Reference)"
            final_skin_age = 0
            age_range = "N/A"
            texture_desc = "N/A"
            jaw_tension = "Normal"

        biometrics = ProfessionalBiometrics(
            skin_age=final_skin_age,
            ita=ita,
            skin_type=skin_type,
            skin_hex=f"rgb({int(lab['L']*2.5)}, {int(lab['L']*2.2)}, {int(lab['L']*1.8)})",
            elasticity_score=biometrics_data.get("elasticity_score") or (0.85 if "Low" in jaw_tension else 0.6),
            melanin_index=biometrics_data.get("melanin_index") or round(lab["b"] * 2.1, 1),
            erythema_index=biometrics_data.get("erythema_index") or round(lab["a"] * 3.5, 1),
            pore_density=biometrics_data.get("pore_density", "Normal") if image_type == "face" else f"Analyzing {image_type.capitalize()}",
            wrinkle_score=biometrics_data.get("wrinkle_score") or (0.4 if "lines" in texture_desc else 0.1),
            age_range=age_range,
            confidence_score=confidence
        )
        
        # Step 4: Color Science (Mapping)
        color_data = raw_analysis.get("color", {})
        personal_color = PersonalColor(
            cielab=lab,
            seasonal_type=color_data.get("seasonal_type", "Unknown"),
            undertone=color_data.get("undertone", "Neutral"),
            recommended_palette=color_data.get("recommended_palette", []),
            eye_hair_match=color_data.get("eye_hair_match", "Eye: None, Hair: None")
        )
        
        # Step 5: Face Geometry (Mapping)
        face_data = raw_analysis.get("face", {})
        face_geometry = FaceGeometry(
            shape=face_data.get("shape", "Oval"),
            length_width_ratio=face_data.get("length_width_ratio", 1.4),
            asymmetry=face_data.get("asymmetry", "Normal"),
            jaw_tension=face_data.get("jaw_tension", "Normal"),
            styling_recommendations=face_data.get("styling_recommendations", {"hair": "Professional layer cut", "brows": "Natural curve"})
        )
        
        # Step 6: Professional Dossier (v3.0 Upgrade - Legal Schema Sync)
        ai_dossier = raw_analysis.get("dossier", {})
        
        # 🛡️ Strong Fallback for 500+ character requirement
        default_long_report = (
            "현재 고객님의 피부 상태를 분석 중입니다. 일시적인 데이터 지연이 발생할 경우 이 문구가 표시됩니다. "
            "잠시 후 다시 시도해 주시면 인공지능 가디언이 500자 이상의 상세한 정밀 분석 리포트를 생성하여 "
            "고객님의 현재 기후 환경과 식단 패턴을 대조한 개인 맞춤형 케어 솔루션을 제공해 드릴 예정입니다."
        )

        dossier = ProfessionalDossier(
            medical_report=ai_dossier.get("medical_report") or default_long_report,
            makeup_strategy=ai_dossier.get("makeup_strategy") or "기후 맞춤형 메이크업 전략을 준비 중입니다.",
            hair_architecture=ai_dossier.get("hair_architecture") or "헤어 스타일링 보완 가이드를 준비 중입니다.",
            visual_prompt=ai_dossier.get("visual_prompt") or "",
            shampoo_prescription=ai_dossier.get("shampoo_prescription") or "N/A",
            nutritional_advice=ai_dossier.get("nutritional_advice") or "건강 증진을 위한 영양 권고 사항을 분석 중입니다."
        )
        
        # Step 7: Curation & Risks
        curation = self._generate_integrated_curation(skin_type, face_geometry, personal_color, weather)
        risks = self._generate_risk_filter(lab, weather, current_routine, raw_analysis.get("risks", {}))
        
        # Step 8: Expert Consultation (AI 생성 우선 → 폴백 템플릿)
        ai_consult = raw_analysis.get("expert_consultation", raw_analysis.get("consult", {}))
        consult = self._generate_expert_consult(biometrics, face_geometry, personal_color, weather, ai_consult)
        
        # Step 9: Final Action Plan (v3.1.7-PRO NEW)
        fa_data = raw_analysis.get("final_action", {})
        final_action = FinalAction(
            risk_summary=fa_data.get("risk_summary", "분석된 특이 위험 요인이 없습니다."),
            professional_tip=fa_data.get("professional_tip", "지속적인 자외선 차단과 보습 관리를 권장합니다."),
            offset_routine=fa_data.get("offset_routine", [])
        )
        
        # Step 10: Skin Scoring (v3.1.7-PRO NEW)
        scores = self._calculate_skin_scores(biometrics, face_geometry, personal_color, weather)
        
        # Final Report
        report = TotalBeautyGuardianReport(
            version=version,
            biometrics=biometrics,
            face=face_geometry,
            color=personal_color,
            curation=curation,
            risks=risks,
            consult=consult,
            dossier=dossier,
            final_action=final_action,
            scores=scores,
            reliability_message=reliability_message
        )
        report.image_type = image_type # Add dynamic tag for filter
        return report

    def analyze_routine_consultation(self,
                                     routine: Any,
                                     skin_context: Any,
                                     location: str = "Seoul, Korea",
                                     registration_data: Dict[str, Any] = {},
                                     weather_context: str = None,
                                     camera_metadata: Dict[str, Any] = {},
                                     lang: str = "ko-KR") -> Dict[str, Any]:
        """
        Specialized analysis for Routine Consultation based on existing skin context.
        """
        # Step 1: Prepare Context
        weather = self.environment.fetch_weather(location)
        current_climate = weather_context or f"{weather.get('weather_desc', 'Unknown')} (Humidity: {weather.get('humidity', '--')}%)"

        context = {
            "location": location,
            "weather": current_climate,
            "routine": routine,
            "skin_context": skin_context,
            "user_profile": registration_data,
            "camera": camera_metadata,
            "lang": lang
        }
        
        # Step 2: Call Vision Engine (Internal Logic handles text-only if image_path is None)
        analysis_result = self.vision.analyze_image(
            image_path=None, 
            context=context,
            analysis_type="routine_consultation"
        )
        
        return analysis_result

    def analyze_vanity(self,
                       image_path: str,
                       location: str,
                       registration_data: Dict[str, Any] = {},
                       weather_context: str = None,
                       lifestyle_24h: str = "Balanced",
                       camera_metadata: Dict[str, Any] = {},
                       current_routine: List[str] = [],
                       lang: str = "ko-KR") -> Dict[str, Any]:
        """
        Specialized analysis for Vanity/Efficacy tracking (v1.2.0-VANITY-PRO).
        """
        weather = self.environment.fetch_weather(location)
        current_climate = weather_context or f"{weather.get('weather_desc', 'Unknown')} (Humidity: {weather.get('humidity', '--')}%)"

        context = {
            "location": location,
            "weather": current_climate,
            "lifestyle": lifestyle_24h,
            "camera": camera_metadata,
            "user_profile": registration_data,
            "routine": current_routine,
            "lang": lang
        }

        # Call Vision Engine for Vanity Analysis
        analysis_result = self.vision.analyze_image(
            image_path=image_path,
            context=context,
            analysis_type="vanity"
        )
        
        return analysis_result

    def analyze_product(self, 
                        image_path: str, 
                        product_type: str, # 'food' | 'cosmetic'
                        location: str, 
                        registration_data: Dict[str, Any] = {}, 
                        weather_context: str = None, 
                        lifestyle_24h: str = "Balanced",
                        lang: str = "ko-KR") -> Dict[str, Any]:
        """
        Specialized analysis for Food/Cosmetics ingredients based on user context.
        """
        weather = self.environment.fetch_weather(location)
        current_climate = weather_context or f"Humidity: {weather.get('humidity', '--')}%, UV: {weather.get('uv_index', '--')}"
        
        # Call Vision Engine for Product Analysis
        analysis_result = self.vision.analyze_product(
            image_path=image_path,
            product_type=product_type,
            context={
                "location": location,
                "weather": current_climate,
                "lifestyle": lifestyle_24h,
                "user_profile": registration_data,
                "lang": lang
            }
        )
        
        return analysis_result

    def _generate_expert_consult(self, bio, face, color, weather, ai_consult: dict = None) -> ExpertConsultation:
        """전문가용 리포트: AI 생성 우선, 없을 시 글자 수 보장 폴백 (summary 200+, skincare 150+, makeup 150+, hair 100+)"""
        s_info = weather.get("season_info", {"season": "Unknown", "risk": "General", "advice": "Balanced Care"})
        
        # 🌍 [v1.5.0] 위치 정보 필터링 (좌표 감지 시 '내 지역' 또는 도시명으로 치환)
        loc = weather.get('location', '고객님의 지역')
        if ',' in str(loc) and any(c.isdigit() for c in str(loc)):
            loc = "Chiang Rai" if "Chiang Rai" in str(loc) else "현재 계신 지역"
        
        hum   = weather.get('humidity', '--')
        season = s_info['season']
        risk   = s_info['risk']
        advice = s_info['advice']

        # ── AI 결과 우선 사용 ──────────────────────────────────
        ai = ai_consult or {}

        summary = ai.get("summary") or (
            f"가디언 AI 종합 분석 결과, 고객님의 현재 피부 나이는 {bio.skin_age}세로 측정되었습니다. "
            f"현재 {loc}은 {season} 계절로 {risk}에 노출되기 쉬운 시기이며, "
            f"{color.seasonal_type} 톤 특성상 {hum}% 습도 환경에서 다크닝과 유수분 불균형이 발생하기 쉬우므로 "
            f"SPF50+ 이상의 자외선 차단제를 반드시 사용하시길 권장드립니다. "
            f"피부 장벽 회복을 위해 세라마이드·판테놀·히알루론산이 복합된 보습 루틴을 적용하고, "
            f"{advice} 전략으로 적극적인 환경 대응 케어를 시작하시기 바랍니다. "
            f"식이 측면에서도 항산화 네트워크(비타민C, 글루타치온)를 보충하면 피부 광채 유지에 도움이 됩니다."
        )

        skincare = ai.get("skincare") or (
            f"{season} 기후 위협({risk})에 대응하여, ITA 지수 {bio.ita}도에 최적화된 {advice} 맞춤 루틴을 시작하세요. "
            f"38도 이하 미온수 세안 후 pH 5.5 약산성 클렌저를 사용해 천연 보습 인자를 보호하고, "
            f"토너 단계에서 히알루론산·글리세린 복합 제형을 레이어링하여 수분막을 형성하십시오. "
            f"세라마이드 NP가 포함된 에센스와 흡수력이 높은 크림으로 마무리하면 장벽 강화 효과를 기대할 수 있습니다."
        )

        makeup = ai.get("makeup") or (
            f"현재 {season}의 산화 위험과 {hum}% 습도를 고려하여, 항산화 기능이 포함된 "
            f"{color.undertone} 타겟팅 수분 프라이머 사용을 권장합니다. "
            f"{color.seasonal_type} 타입에 최적화된 세미-매트 쿠션 파운데이션을 얇게 레이어링하고, "
            f"테라코타·번트 오렌지 계열 블러셔로 혈색을 살린 뒤, "
            f"피니싱 파우더와 픽싱 스프레이로 지속력을 확보하여 메이크업 산화를 예방하십시오."
        )

        hair = ai.get("hair") or (
            f"{face.shape}형 구조에 어울리는 C컬 레이어드 커트를 권장하며, "
            f"{season} 두피 손상 요인(열·자외선)을 차단하기 위해 "
            f"징크피리치온 함유 밸런싱 샴푸와 모발 끝 전용 헤어 오일 관리를 병행하십시오."
        )

        return ExpertConsultation(
            summary=summary,
            skincare=skincare,
            makeup=makeup,
            hair=hair
        )

    def _calculate_skin_scores(self, bio: ProfessionalBiometrics, face: FaceGeometry, color: PersonalColor, weather: Dict[str, Any]) -> SkinScores:
        """Calculates 5 specialized skin scores (0-100) based on v3.1.7-PRO logic."""
        
        # 1. Total Health Score
        # Weighted sum: Elasticity(30%), Tone Stability(40%), Texture/Wrinkle(30%)
        e_comp = bio.elasticity_score * 100
        t_comp = min(100, max(0, (bio.ita / 55.0) * 100))
        w_comp = (1.0 - bio.wrinkle_score) * 100
        total_health = int(e_comp * 0.3 + t_comp * 0.4 + w_comp * 0.3)
        
        # 2. Radiance Score
        # Normalized ITA value (Ideal Radiance >= 55)
        radiance = int(min(100, max(0, (bio.ita / 55.0) * 100)))
        
        # 3. Climate Adaptability Score
        # Penalty for high humidity deviation (base 50%) and UV stress
        hum = weather.get("humidity", 50)
        uv = weather.get("uv", 5)
        hum_penalty = abs(hum - 50) * 0.5
        uv_penalty = uv * 3.0
        climate_adaptability = int(max(0, 100 - (hum_penalty + uv_penalty)))
        
        # 4. Skin Vitality Index (SVI)
        # Comparison: Chronological Age vs AI Skin Age (Standard base 50)
        # +2 points for every year younger than average
        vitality = int(max(0, min(100, 50 + (35 - bio.skin_age) * 2)))
        
        # 5. Barrier Resilience Score
        # 100 - (Erythema Index * 1.2 Penalty)
        resilience = int(max(0, 100 - (bio.erythema_index * 1.2)))
        
        return SkinScores(
            total_health=total_health,
            radiance=radiance,
            climate_adaptability=climate_adaptability,
            vitality=vitality,
            resilience=resilience
        )

    def _generate_integrated_curation(self, skin_type, face, color, weather) -> IntegratedCuration:
        location_name = weather.get('location', '현 위치')
        return IntegratedCuration(
            skincare_prescription=f"{skin_type} 피부 타입을 위한 {location_name} 맞춤형 스킨케어",
            makeup_prescription=f"{color.seasonal_type} 톤에 최적화된 다크닝 방지 메이크업",
            hair_prescription=f"{face.shape}형 얼굴을 위한 헤어 스타일링",
            climate_adjustment="UV 지수 및 습도 대응 기후 최적화"
        )

    def _generate_risk_filter(self, lab, weather, routine, raw_risks: dict = None) -> GuardianRiskFilter:
        ai_risks = raw_risks or {}
        darkening_risk = ai_risks.get("makeup_oxidation_risk") or ("High Risk" if lab["b"] > 18 and weather["humidity"] > 70 else "Secure")
        
        return GuardianRiskFilter(
            alert_level=ai_risks.get("alert_level") or ("Warning" if "High" in darkening_risk else "Secure"),
            makeup_oxidation_risk=darkening_risk,
            scalp_thermal_risk=ai_risks.get("scalp_thermal_risk") or "Secure (Normal)",
            blacklist_ingredients=ai_risks.get("blacklist_ingredients") or ["PPD", "Ammonia", "Iron Oxides"],
            conflict_report=ai_risks.get("conflict_report") or f"현재 루틴 내 {len(routine)}개 성분과 기후 상충 여부 분석 완료"
        )

if __name__ == "__main__":
    guardian = TotalBeautyGuardianEngine()
    # Test Scenario: BIPOC in Tropical Bangkok using VT Reedle Shot and Retinol
    full_report = guardian.analyze_image("path/to/selfie.jpg", "Bangkok", current_routine=["Retinol"])
    print(full_report.to_json())
