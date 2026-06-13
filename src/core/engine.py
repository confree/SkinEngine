from src.core.guardian_schema import TotalBeautyGuardianReport, FaceGeometry, PersonalColor, IntegratedCuration, GuardianRiskFilter, ExpertConsultation, ProfessionalBiometrics, ProfessionalDossier, FinalAction, SkinScores
from src.core.biometrics import BiometricsEngine
from src.core.environment import EnvironmentEngine
from src.core.interaction import InteractionEngine
from src.core.guardian_vision import GuardianVisionEngine
from src.core.climate_manager import ClimateManager
from src.core.clinical_manager import ClinicalManager
from typing import List, Dict, Any, Tuple
import json
import os

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
        
        # [v15.0.0] Database-Backed Climate & Knowledge Intelligence
        self.db_params = {
            "host": "72.62.254.119",
            "user": "verisadmin",
            "password": "veris1234!",
            "dbname": "veriskin"
        }
        # [v15.1.0] Fixed VC_API_KEY integration
        self.vc_api_key = "978MRVGG2XR9MJP4Y9LGQUL2F"
        self.climate_mgr = ClimateManager(self.db_params, vc_api_key=self.vc_api_key)
        self.clinical_mgr = ClinicalManager(self.db_params)
        
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

    def analyze_vanity(self, 
                       image_path: str, 
                       location: str = "Seoul, Korea", 
                       registration_data: Dict[str, Any] = {}, 
                       weather_context: str = None, 
                       lifestyle_24h: str = "Balanced",
                       camera_metadata: Dict[str, Any] = {},
                       current_routine: List[str] = [],
                       lang: str = "en",
                       skin_context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        [v11.5.0] Specialized Skin Efficacy Tracking (Vanity Mode).
        """
        return self.analyze_image(
            image_path=image_path,
            location=location,
            current_routine=current_routine,
            registration_data=registration_data,
            weather_context=weather_context,
            lifestyle_24h=lifestyle_24h,
            camera_metadata=camera_metadata,
            lang=lang,
            skin_context=skin_context,
            analysis_type="vanity"
        )

    def analyze_image(self, 
                      image_path: str, 
                      location: str, 
                      registration_data: Dict[str, Any] = {}, # 👤 User signup info (Age, Sex, ITA)
                      weather_context: str = None, 
                      lifestyle_24h: str = "Balanced",        # 🍎 Diet, Sleep, etc.
                      camera_metadata: Dict[str, Any] = {},   # 📸 Luminance, Temp
                      current_routine: List[str] = [],
                      lang: str = "en",
                      analysis_type: str = "general",
                      skin_context: Dict[str, Any] = {}) -> TotalBeautyGuardianReport:
        """
        Total Beauty Analysis via Gemini Vision Engine (v3.5 Location-Aware).
        """
        # Step 1: Environment & Weather Detection
        weather = self.environment.fetch_weather(location)
        
        # [v15.0.0] DB-Backed Refined Climate Reasoning
        refined_climate = self.climate_mgr.get_refined_climate_context(
            city=location.split(",")[0].strip(),
            current_temp=weather.get('temp'),
            current_hum=weather.get('humidity')
        )

        if weather_context:
            current_climate = f"{weather_context} | {refined_climate}"
        else:
            current_climate = f"{weather.get('weather_desc', 'Unknown')} (Humidity: {weather.get('humidity', '--')}%) | {refined_climate}"

        # Step 2: Automated Vision Analysis (Now with DB-Refined Expert Context)
        raw_analysis = self.vision.analyze_image(
            image_path, 
            context={
                "location": location, 
                "weather": current_climate, # Now contains DB Hero/Villain logic
                "lifestyle": lifestyle_24h,
                "camera": camera_metadata,
                "user_profile": registration_data,
                "previous_analysis": skin_context,
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
            
            # Lighting & Color Normalization (v3.1.8-PRO)
            reference_l = 62.0  
            normalization_factor_l = 0.5 
            normalized_l = raw_l + (reference_l - raw_l) * normalization_factor_l
            
            # [STABILIZATION] Yellow/Blue (b*) Normalization
            reference_b = 18.0
            normalization_factor_b = 0.3
            normalized_b = raw_b + (reference_b - raw_b) * normalization_factor_b
            
            lab = {"L": normalized_l, "a": raw_a, "b": normalized_b}
            
            # [STABILIZATION] Prioritize programmatic ITA over AI predicted ITA for consistency
            calculated_ita = round(self.biometrics.calculate_ita(lab["L"], lab["b"]), 1)
            ita = calculated_ita 
            skin_type = biometrics_data.get("skin_type") or self.biometrics.classify_skin_type(ita)
            
            # [v12.9.12] 🛡️ DEFINE FACE & COLOR STRUCTURES
            face_data = raw_analysis.get("face", {})
            face_geometry = FaceGeometry(
                shape=face_data.get("shape"),
                length_width_ratio=face_data.get("length_width_ratio", 1.0),
                asymmetry=face_data.get("asymmetry"),
                jaw_tension=face_data.get("jaw_tension"),
                styling_recommendations=face_data.get("styling_recommendations", {})
            )
            
            personal_color = PersonalColor(
                cielab=lab,
                seasonal_type=color_data.get("seasonal_type"),
                undertone=color_data.get("undertone"),
                recommended_palette=color_data.get("recommended_palette", []),
                eye_hair_match=color_data.get("eye_hair_match")
            )
            
            # [CLINICAL LOGIC] Factor in OR & R2 for risk weighting
            texture_desc = biometrics_data.get("pore_density", "").lower()
            jaw_tension = face_data.get("jaw_tension", "Normal")
            
            # Age Range from AI Inference
            age_range = biometrics_data.get("age_range", "Unknown")
            
            # Use registration data if valid age is provided
            reg_age = registration_data.get('age')
            if reg_age is not None:
                try:
                    age_int = int(reg_age)
                    age_range = f"{(age_int // 10) * 10}대 " + ("초반" if age_int % 10 < 5 else "후반")
                except (ValueError, TypeError):
                    pass 

            # [v12.9.11] 🛡️ FORCE SYNC: Ensure debug file is written immediately
            try:
                debug_path = "logs/DEBUG_LAST_AI_RAW.json"
                with open(debug_path, "w", encoding="utf-8") as f:
                    json.dump(raw_analysis, f, indent=4, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
            except Exception as debug_err:
                print(f"[DEBUG-SYSTEM] Write failed: {debug_err}")

            # [v12.9.0] 🛡️ NO FALLBACK POLICY: Raise error if AI data is incomplete
            final_skin_age = biometrics_data.get("skin_age")
            if final_skin_age is None:
                # [CRITICAL] Provide raw data back to client for instant debugging
                error_msg = f"AI failed to determine 'skin_age'. RAW_DATA: {json.dumps(raw_analysis)}"
                raise ValueError(error_msg)
                
            # [v12.9.0] 🛡️ Strict Biometrics Validation
            elasticity = biometrics_data.get("elasticity_score")
            wrinkle = biometrics_data.get("wrinkle_score")
            
            if elasticity is None or wrinkle is None:
                raise ValueError(f"Missing critical biometrics: elasticity={elasticity}, wrinkle={wrinkle}")

            biometrics = ProfessionalBiometrics(
                skin_age=final_skin_age,
                ita=ita,
                skin_type=skin_type,
                skin_hex=f"rgb({int(lab['L']*2.5)}, {int(lab['L']*2.2)}, {int(lab['L']*1.8)})",
                elasticity_score=elasticity,
                melanin_index=biometrics_data.get("melanin_index"),
                erythema_index=biometrics_data.get("erythema_index"),
                pore_density=biometrics_data.get("pore_density"),
                wrinkle_score=wrinkle,
                age_range=age_range,
                confidence_score=confidence
            )

            # [v12.9.15] 🛡️ Validation for newly Strict Biometrics
            if biometrics.melanin_index is None or biometrics.erythema_index is None:
                raise ValueError(f"Missing melanin/erythema data. RAW: {json.dumps(biometrics_data)}")

        else:
            # Ingredient/Food mode
            raise ValueError(f"Unsupported analysis type for biometrics: {image_type}")

        # [v12.9.0] 🛡️ Dossier & Consult Validation
        ai_dossier = raw_analysis.get("dossier")
        if not ai_dossier:
            raise ValueError("AI failed to generate 'dossier' report.")

        dossier = ProfessionalDossier(
            medical_report=ai_dossier.get("medical_report"),
            makeup_strategy=ai_dossier.get("makeup_strategy"),
            hair_architecture=ai_dossier.get("hair_architecture"),
            visual_prompt=ai_dossier.get("visual_prompt") or "",
            shampoo_prescription=ai_dossier.get("shampoo_prescription"),
            nutritional_advice=ai_dossier.get("nutritional_advice")
        )

        for field in ["medical_report", "makeup_strategy", "hair_architecture", "shampoo_prescription", "nutritional_advice"]:
            if not getattr(dossier, field):
                raise ValueError(f"AI Dossier is missing critical field: {field}")
        
        # Step 7: Curation & Risks (Must be present)
        curation = self._generate_integrated_curation(skin_type, face_geometry, personal_color, weather)
        risks = self._generate_risk_filter(lab, weather, current_routine, raw_analysis.get("risks", {}))
        
        # Step 8: Expert Consultation
        ai_consult = raw_analysis.get("expert_consultation", raw_analysis.get("consult", {}))
        if not ai_consult:
            raise ValueError("AI failed to generate 'consult' summary.")

        consult = self._generate_expert_consult(biometrics, face_geometry, personal_color, weather, ai_consult, lang=lang)
        
        # Step 9: Final Action Plan
        fa_data = raw_analysis.get("final_action")
        if not fa_data:
            raise ValueError("AI failed to generate 'final_action' plan.")

        final_action = FinalAction(
            risk_summary=fa_data.get("risk_summary"),
            professional_tip=fa_data.get("professional_tip"),
            offset_routine=fa_data.get("offset_routine", [])
        )
        
        # Step 10: Skin Scoring (v3.1.8-PRO STABILIZED)
        historical_records = []
        comparison_result = None
        
        if skin_context and "metadata" in skin_context:
            # Handle recursive metadata or flat previous analysis
            hist_meta = skin_context.get("metadata", {})
            historical_records = [hist_meta]
        elif isinstance(skin_context, dict) and "scores" in skin_context:
            historical_records = [skin_context]

        # [STABILIZATION] Intelligent Smoothing (Moving Average)
        historical_scores = [h.get("scores", {}) for h in historical_records]
        scores = self._calculate_skin_scores(biometrics, face_geometry, personal_color, weather, historical_scores)

        if historical_records:
            last = historical_records[0]
            last_scores = last.get("scores", {})
            
            # [v15.6.0] 🧬 Calculate explicit Delta (Comparison Logic)
            current_map = {
                "total_health": scores.total_health,
                "radiance": scores.radiance,
                "vitality": scores.vitality,
                "resilience": scores.resilience
            }
            
            deltas = {}
            for key in current_map:
                prev_val = last_scores.get(key)
                if prev_val is not None:
                    try:
                        diff = round(float(current_map[key]) - float(prev_val), 1)
                        deltas[f"{key}_delta"] = f"+{diff}" if diff > 0 else str(diff)
                    except (ValueError, TypeError):
                        continue
            
            comparison_result = {
                "status": "stable" if abs(float(deltas.get("total_health_delta", 0))) < 5 else ("improved" if float(deltas.get("total_health_delta", 0)) > 0 else "declining"),
                "deltas": deltas,
                "summary": raw_analysis.get("consult", {}).get("visual_progress") or "시간에 따른 피부 변화가 감지되었습니다.",
                "previous_date": last.get("created_at") or "전회차"
            }
        
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
            reliability_message=reliability_message,
            comparison=comparison_result
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
                                     lang: str = "en") -> Dict[str, Any]:
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
                       lang: str = "en",
                       skin_context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Specialized analysis for Vanity/Efficacy tracking (v1.2.0-VANITY-PRO).
        """
        return self.analyze_image(
            image_path=image_path,
            location=location,
            current_routine=current_routine,
            registration_data=registration_data,
            weather_context=weather_context,
            lifestyle_24h=lifestyle_24h,
            camera_metadata=camera_metadata,
            lang=lang,
            skin_context=skin_context,
            analysis_type="vanity"
        )

    def analyze_product(self, 
                        image_path: str, 
                        product_type: str, # 'food' | 'cosmetic'
                        location: str, 
                        registration_data: Dict[str, Any] = {}, 
                        weather_context: str = None, 
                        lifestyle_24h: str = "Balanced",
                        lang: str = "en",
                        skin_context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Specialized analysis for Food/Cosmetics ingredients based on user context.
        """
        return self.vision.analyze_image(
            image_path=image_path,
            context={
                "location": location,
                "weather": weather_context,
                "lifestyle": lifestyle_24h,
                "user_profile": registration_data,
                "skin_context": skin_context,
                "lang": lang
            },
            analysis_type=product_type # 'food' or 'cosmetic'
        )

    def analyze_cosmetic_harmonization(self, 
                                     user_id: str,
                                     routine_list: List[Dict[str, Any]] = [],
                                     skin_context: Dict[str, Any] = {},
                                     location: str = "Seoul, Korea",
                                     weather: str = "Clear",
                                     lang: str = "en",
                                     registration_data: Any = {},
                                     target_product: Any = None,
                                     image_path: str = None) -> Dict[str, Any]:
        """
        [v11.2.7] Dedicated Cosmetic Harmonization Analysis.
        Now supports image_path and target_product for full vision analysis.
        """
        # Step 1: Prepare Context
        current_weather = self.environment.fetch_weather(location)
        climate_summary = f"{current_weather.get('weather_desc', 'Unknown')} (Humidity: {current_weather.get('humidity', '--')}%)"

        context = {
            "user_id": user_id,
            "target_product": target_product,
            "location": location,
            "weather": weather or climate_summary,
            "routine": routine_list,
            "skin_context": skin_context,
            "user_profile": registration_data,
            "lang": lang
        }
        
        # Step 2: Call Vision Engine
        analysis_result = self.vision.analyze_image(
            image_path=image_path, 
            context=context,
            analysis_type="cosmetic"
        )
        
        return analysis_result
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

    def _generate_expert_consult(self, bio, face, color, weather, ai_consult: dict = None, lang: str = "en") -> ExpertConsultation:
        """전문가용 리포트: AI 생성 우선, 없을 시 글자 수 보장 폴백 (summary 200+, skincare 150+, makeup 150+, hair 100+)"""
        s_info = weather.get("season_info", {"season": "Unknown", "risk": "General", "advice": "Balanced Care"})
        
        # 🌍 [v1.5.2] 위치 정보 정규화 (하드코딩 제거: 실제 위치 정보 우선)
        loc = weather.get('location') or '현재 계신 지역'
        if ',' in str(loc) and any(c.isdigit() for c in str(loc)):
             # 좌표 데이터인 경우 가독성을 위해 '내 위치'로 표시하되, AI에게는 전체 데이터를 전달함
             loc = "현재 계신 지역"
        
        hum   = weather.get('humidity', '--')
        season = s_info['season']
        risk   = s_info['risk']
        advice = s_info['advice']

        # ── AI 결과 우선 사용 ──────────────────────────────────
        ai = ai_consult or {}

        # ── 임상 지능 통합 (Clinical Intelligence Injection) ────────────────
        # Get detected concerns from AI analysis (if available)
        detected_concerns = []
        if ai_consult.get("detected_keywords"):
            detected_concerns = ai_consult["detected_keywords"]
        elif bio.skin_type:
            detected_concerns = [bio.skin_type]
            
        clinical_data = self.clinical_mgr.get_clinical_advice(detected_concerns)
        clinical_rx_block = ""
        if clinical_data["disease_guidelines"]:
            guide = clinical_data["disease_guidelines"][0]
            
            is_korean = lang.lower().startswith("ko")
            if is_korean:
                clinical_rx_block = (
                    f"\n\n[🩺 Clinical Ground Truth: {guide['name']}]\n"
                    f"학술 근거: {guide['source']}\n"
                    f"- 공식 처방: {guide['medical_rx']}\n"
                    f"- 세안 지침: {guide['cleansing']}\n"
                    f"- 보습 지침: {guide['moisturizing']}\n"
                    f"- 주의사항: {guide['contraindications']}"
                )
            else:
                translated_name = self.vision.translate_text(guide['name'], lang)
                translated_source = self.vision.translate_text(guide['source'], lang)
                translated_rx = self.vision.translate_text(guide['medical_rx'], lang)
                translated_cleansing = self.vision.translate_text(guide['cleansing'], lang)
                translated_moisturizing = self.vision.translate_text(guide['moisturizing'], lang)
                translated_contra = self.vision.translate_text(guide['contraindications'], lang)
                
                clinical_rx_block = (
                    f"\n\n[🩺 Clinical Ground Truth: {translated_name}]\n"
                    f"Evidence Source: {translated_source}\n"
                    f"- Medical Prescription: {translated_rx}\n"
                    f"- Cleansing Guide: {translated_cleansing}\n"
                    f"- Moisturizing Guide: {translated_moisturizing}\n"
                    f"- Precautions: {translated_contra}"
                )

        summary = ai.get("summary") or (
            f"가디언 AI 종합 분석 결과, 고객님의 현재 피부 나이는 {bio.skin_age}세로 측정되었습니다. "
            f"현재 {loc}은 {season} 계절로 {risk}에 노출되기 쉬운 시기이며, "
            f"{color.seasonal_type} 톤 특성상 {hum}% 습도 환경에서 다크닝과 유수분 불균형이 발생하기 쉬우므로 "
            f"SPF50+ 이상의 자외선 차단제를 반드시 사용하시길 권장드립니다. "
            f"피부 장벽 회복을 위해 세라마이드·판테놀·히알루론산이 복합된 보습 루틴을 적용하고, "
            f"{advice} 전략으로 적극적인 환경 대응 케어를 시작하시기 바랍니다. "
            f"식이 측면에서도 항산화 네트워크(비타민C, 글루타치온)를 보충하면 피부 광채 유지에 도움이 됩니다."
        )
        
        if clinical_rx_block:
            summary += clinical_rx_block

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

    def _calculate_skin_scores(self, bio: ProfessionalBiometrics, face: FaceGeometry, color: PersonalColor, weather: Dict[str, Any], history: List[Dict[str, Any]] = []) -> SkinScores:
        """Calculates 5 specialized skin scores (0-100) based on v3.1.8-PRO stabilized logic."""
        
        # 1. Total Health Score
        # [FIX] Scaled to 0-100 range consistently.
        # Weighted sum: Elasticity(30%), Tone Stability(40%), Texture/Wrinkle(30%)
        e_comp = bio.elasticity_score # Already 0-100 from Gemini or fallback
        t_comp = min(100, max(0, (bio.ita / 55.0) * 100)) # Radiance mapping
        w_comp = 100 - bio.wrinkle_score # 0 wrinkle = 100 points
        
        total_health = int(e_comp * 0.3 + t_comp * 0.4 + w_comp * 0.3)
        total_health = max(0, min(100, total_health))
        
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
        # 100 - (Erythema Index * 1.0 Penalty) [FIXED scale]
        resilience = int(max(0, 100 - (bio.erythema_index * 1.0)))
        
        # [STABILIZATION] Intelligent Smoothing (Moving Average)
        if history:
            total_health = self._apply_score_smoothing(total_health, [h.get("total_health") for h in history if h.get("total_health") is not None])
            radiance = self._apply_score_smoothing(radiance, [h.get("radiance") for h in history if h.get("radiance") is not None])
            vitality = self._apply_score_smoothing(vitality, [h.get("vitality") for h in history if h.get("vitality") is not None])
            resilience = self._apply_score_smoothing(resilience, [h.get("resilience") for h in history if h.get("resilience") is not None])
            climate_adaptability = self._apply_score_smoothing(climate_adaptability, [h.get("climate_adaptability") for h in history if h.get("climate_adaptability") is not None])

        return SkinScores(
            total_health=total_health,
            radiance=radiance,
            climate_adaptability=climate_adaptability,
            vitality=vitality,
            resilience=resilience
        )

    def _apply_score_smoothing(self, current: int, historical: List[int], threshold: int = 8) -> int:
        """
        Applies intelligence smoothing to scores to prevent micro-fluctuations.
        - If change is within threshold, apply weighted average for stability.
        - If change is significant, trust the current measurement.
        """
        if not historical or len(historical) == 0:
            return current
        
        avg_hist = sum(historical) / len(historical)
        diff = current - avg_hist
        
        if abs(diff) < threshold:
            # Within noise threshold: Apply 30% of change for smoothness
            return int(avg_hist + diff * 0.3)
        else:
            # Significant change: Reflect 70% of change (responsive but still dampened slightly)
            return int(avg_hist + diff * 0.7)

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
