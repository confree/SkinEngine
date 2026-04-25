from google import genai
from google.genai import types
from PIL import Image
import io
import json
import base64
import hashlib
import os
import datetime
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# [v8.8.4] Load environment variables
load_dotenv()

class GuardianVisionEngine:
    """
    [Guardian-Vision-v3.5]
    Kbeauty-Proven Architecture: SDK + Pillow + models/ Prefix.
    Restores real-time AI connectivity using the success pattern from 2 days ago.
    """
    
    def __init__(self, api_key: str = None):
        # [SECURITY] Use environment variable with fallback for legacy support
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Gemini API Key is missing. Please set GEMINI_API_KEY in .env file.")
        
        self.client = genai.Client(api_key=self.api_key)
        
        # [VERSION v4.1 - STABLE] 
        self.model_id = 'models/gemini-2.5-flash'
        print(f"[READY] [AI-Engine] VeriSkin Guardian Ready: Targeting {self.model_id}")
        
        # [ULTRA-STRICT ANALYSIS v3.1.8 - ENFORCED]
        self.system_instruction = (
            "당신은 반드시 다음의 JSON 구조만을 반환해야 하는 '전문 Skin 분석기'입니다.\n\n"
            "### [필수 JSON 구조 - 반드시 이 키값들을 포함할 것]\n"
            "{\n"
            "  \"version\": \"3.1.8-PRO\",\n"
            "  \"image_type\": \"face\",\n"
            "  \"biometrics\": {\n"
            "    \"skin_age\": [현재 나이를 반영한 정수],\n"
            "    \"elasticity_score\": [0-100 float],\n"
            "    \"wrinkle_score\": [0-100 float],\n"
            "    \"ita\": 35.0, \"skin_type\": \"건성\", \"skin_hex\": \"#FFFFFF\", \"melanin_index\": 40.0, \"erythema_index\": 20.0, \"pore_density\": \"Normal\", \"age_range\": \"50s\", \"confidence_score\": 90\n"
            "  },\n"
            "  \"face\": { \"shape\": \"Oval\", \"length_width_ratio\": 1.4, \"asymmetry\": \"None\", \"jaw_tension\": \"Normal\", \"styling_recommendations\": { \"hair\": \"Short\", \"brows\": \"Straight\" } },\n"
            "  \"color\": { \"cielab\": { \"L\": 65.0, \"a\": 10.0, \"b\": 20.0 }, \"seasonal_type\": \"Spring\", \"undertone\": \"Warm\", \"recommended_palette\": [], \"eye_hair_match\": \"Good\" },\n"
            "  \"curation\": { \"skincare_prescription\": \"Moisturize\", \"makeup_prescription\": \"Glow\", \"hair_prescription\": \"Volume\", \"climate_adjustment\": \"Hydrate\" },\n"
            "  \"consult\": { \"summary\": \"String\", \"skincare\": \"String\", \"makeup\": \"String\", \"hair\": \"String\", \"visual_progress\": \"String\", \"lifestyle_causality\": \"String\", \"efficacy\": [], \"conflicts\": [], \"detected_keywords\": [\"Acne\", \"Redness\", \"Pores\"] },\n"
            "  \"dossier\": { \"medical_report\": \"String\", \"makeup_strategy\": \"String\", \"hair_architecture\": \"String\", \"visual_prompt\": \"String\", \"shampoo_prescription\": \"String\", \"nutritional_advice\": \"String\" },\n"
            "  \"final_action\": { \"offset_routine\": [], \"professional_tip\": \"String\", \"future_prediction\": {}, \"peer_context\": \"String\" },\n"
            "  \"scores\": { \"total_health\": 75, \"radiance\": 75, \"climate_adaptability\": 75, \"vitality\": 75, \"resilience\": 75 }\n"
            "}\n\n"
            "### [중요 지침]\n"
            "1. `biometrics` 내의 모든 수치는 반드시 0.0-100.0 사이의 숫자로 채우십시오.\n"
            "2. 사용자의 실제 나이가 50세라면 `skin_age`는 45~55 사이의 숫자로 반드시 추정하여 기입하십시오.\n"
            "3. 절대 '알 수 없음'이나 '데이터 없음'으로 필드를 생략하지 마십시오. 추정치라도 반드시 넣어야 합니다.\n"
            "4. `dossier` 내의 모든 리포트 내용은 300자 이상의 풍부한 한국어로 작성하십시오.\n"
            "5. **[임상 매칭]**: `consult` 항목의 `detected_keywords`에는 '여드름', '아토피', '홍조', '건조', '민감' 등 관찰된 주요 피부 고민 키워드를 2~3개 반드시 포함하십시오.\n"
            "6. 이전 버전(1.2.1)의 양식을 절대 사용하지 마십시오. 오직 위 구조만 허용됩니다."
        )

        # [VANITY/EFFICACY ANALYSIS v1.2.1-VANITY-PRO]
        self.vanity_instruction = (
            "귀하는 사용자의 피부 변화를 정밀하게 추적하고 제품의 효능을 입증하는 '임상 뷰티 가디언'입니다.\n"
            "**[v1.2.1-VANITY-PRO 루틴 효능 분석 지침]**:\n"
            "1. **환경 보정**: 이전 촬영 데이터(`skin_context`)가 있을 경우, 현재 이미지와 조명 상태를 대조하여 조명 차이에 의한 오차를 감안한 뒤 순수한 피부 변화값(1~2% 내외)을 산출하십시오.\n"
            "2. **수치 엄격성**: 모든 점수와 변화율은 **0-100** 범위를 준수하십시오.\n"
            "3. **인과 관계 추론**: 루틴 성분과 생활 방식이 현재 피부 변화에 준 영향을 분석하십시오.\n"
            "4. **효능 입증**: 현재 루틴의 효능을 궁합 점수로 환산하십시오.\n"
            "**[응답 형식]**: JSON 구조 엄수.\n"
            "{\n"
            "  \"analysis_id\": \"UUID-V10-SYNC\",\n"
            "  \"compatibility_score\": int,\n"
            "  \"version\": \"1.2.1-VANITY-PRO\",\n"
            "  \"scores\": { \"total_health\": int, \"radiance\": int, \"vitality\": int, \"resilience\": int, \"climate_adaptability\": int },\n"
            "  \"consult\": {\n"
            "    \"summary\": \"string\",\n"
            "    \"skincare\": \"string\",\n"
            "    \"visual_progress\": \"string\",\n"
            "    \"lifestyle_causality\": \"string\",\n"
            "    \"efficacy\": [{ \"target\": \"string\", \"reason\": \"string\" }],\n"
            "    \"conflicts\": [{ \"item_a\": \"string\", \"item_b\": \"string\", \"warning\": \"string\" }]\n"
            "  },\n"
            "  \"final_action\": {\n"
            "    \"offset_routine\": [\"string\"],\n"
            "    \"professional_tip\": \"string\",\n"
            "    \"future_prediction\": { \"expected_milestone\": \"string\", \"estimated_days\": int, \"maintenance_priority\": \"string\" },\n"
            "    \"peer_context\": \"string\"\n"
            "  }\n"
            "}\n"
        )
        
        # [PRODUCT ANALYSIS v3.1.8 - PRO LIVE]
        self.product_instruction = (
            "귀하는 사용자의 피부 장벽을 수호하는 '스마트 뷰티 가디언'입니다.\n"
            "**[v3.1.8-PRO 정밀 분석 지침]**:\n"
            "1. **언어 규칙**: 모든 응답은 사용자가 요청한 언어로만 작성하십시오.\n"
            "2. **제품 분석**: OCR을 통해 제품명, 브랜드, 성분 추출.\n"
            "3. **궁합 분석**: 피부 타입 및 기후와의 상충 관계 분석.\n"
            "4. **[중요] 모호성 배제**: 사진이 흐릿하거나 조명이 부족하여 제품을 명확하게 식별할 수 없는 경우, 절대 추측하여 분석하지 마십시오. 대신 `final_action.risk_summary`와 `consult.summary`에 '사진이 명확하지 않아 정밀 분석이 불가능합니다'라고 명시하십시오.\n"
            "**[응답 형식]**: JSON 구조 엄수.\n"
            "{\n"
            "  \"version\": \"3.1.8-PRO\",\n"
            "  \"image_type\": \"cosmetic|food\",\n"
            "  \"title\": \"식별된 제품명 또는 식품명 (확실한 경우에만 작성)\",\n"
            "  \"product_analysis\": { \"item_name\": \"string\", \"key_ingredients\": [], \"brand_name\": \"string\", \"category\": \"string\" },\n"
            "  \"skin_matching\": { \"compatibility_score\": int, \"climate_clash\": \"string\", \"match_reason\": \"string\", \"warning_ingredients\": [] },\n"
            "  \"dossier\": { \"medical_report\": \"string\", \"nutritional_advice\": \"string\" },\n"
            "  \"risks\": { \"conflict_report\": \"string\", \"makeup_oxidation_risk\": \"string\", \"blacklist\": [], \"scalp_caution\": \"string\" },\n"
            "  \"final_action\": { \"risk_summary\": \"string\", \"professional_tip\": \"string\", \"offset_routine\": [] }\n"
            "}\n"
        )

        # [ROUTINE CONSULTATION v1.2.0 - SYNERGY FOCUS]
        self.routine_consultation_instruction = (
            "귀하는 리얼타임 루틴 진단 및 제품 상성 분석 전문가 '스마트 루틴 가디언'입니다.\n"
            "**[v1.2.0-SYNERGY 분석 지침]**:\n"
            "1. **시너비 분석**: 루틴 내 제품들(A+B, B+C 등) 간의 기능적 보완 작용을 분석하여 `synergy_score`를 산출하십시오.\n"
            "2. **성분 충돌**: 레티놀+비타민C, 고농도 AHA+BHA 등 자극을 유발하거나 효능을 상쇄하는 조합을 정밀 추적하십시오.\n"
            "3. **기후-피부 최적화**: 현재 환경(온도, 습도, UV)에 해당 루틴이 얼마나 적합한지 평가하십시오.\n"
            "4. **리스크 요약**: 발견된 핵심 위험 요소를 `risk_summary`에 150자 내외로 기술하십시오.\n"
            "**[응답 형식]**: JSON 구조 엄수.\n"
            "{\n"
            "  \"version\": \"1.2.0-SYNERGY\",\n"
            "  \"image_type\": \"routine\",\n"
            "  \"synergy_score\": int(0-100),\n"
            "  \"consult\": {\n"
            "    \"summary\": \"string\",\n"
            "    \"skincare\": \"string\",\n"
            "    \"efficacy\": [{ \"target\": \"string\", \"reason\": \"string\" }],\n"
            "    \"conflicts\": [{ \"item_a\": \"string\", \"item_b\": \"string\", \"warning\": \"string\" }]\n"
            "  },\n"
            "  \"final_action\": { \"offset_routine\": [], \"professional_tip\": \"string\", \"risk_summary\": \"string\" },\n"
            "  \"scores\": { \"total_health\": int, \"radiance\": int, \"vitality\": int, \"resilience\": int, \"climate_adaptability\": int }\n"
            "}\n"
            "**주의**: `synergy_score`는 반드시 단순 수치(0-100)로 산출하십시오."
        )

        # [COSMETIC HARMONIZATION v1.0.1 - ULTRA STRICT]
        self.cosmetic_instruction = (
            "귀하는 사용자의 현재 피부 상태와 화장품 사이의 화합(Harmony)을 정밀 분석하는 '뷰티 융합 전문가'입니다.\\n"
            "**[v1.0.1-COSMETIC-PRO 분석 지침]**:\\n"
            "1. **이미지 인식 우선**: 만약 'Target Product' 정보가 모호하다면, 첨부된 사진 속의 화장품 라벨, 브랜드명, 전성분표, 혹은 제형을 직접 시각적으로 인식하여 분석하십시오.\\n"
            "2. **[중요] 모호성 배제**: 사진이 흐릿하거나 식별이 어려운 경우 추측하지 마십시오. 명확하지 않을 때는 `consult.summary`에 '사진이 명확하지 않아 분석이 불가능합니다'라고 명확히 기재하십시오.\\n"
            "3. **데이터 부족 시 처리**: 사용자의 피부 타입 정보가 없더라도 기후 정보와 사진 속 피부 상태를 바탕으로 최선의 추정치를 계산하십시오. 다만, 사진 자체의 화질이 문제라면 2번 지침을 따르십시오.\\n"
            "4. **조밀도 및 융합 분석**: 선택된 제품이 사용자 피부 컨디션에 얼마나 잘 융합될지 분석하십시오.\\n"
            "5. **성분-피부 궁합**: 특정 성분이 사용자의 피부 고민에 미칠 긍정적/부정적 영향을 도출하십시오.\\n"
            "**[응답 형식]**: 반드시 아래 JSON 구조 그대로 응답하십시오.\\n"
            "{\\n"
            "  \\\"version\\\": \\\"1.0.0-COSMETIC\\\",\\n"
            "  \\\"image_type\\\": \\\"cosmetic\\\",\\n"
            "  \\\"title\\\": \\\"식별된 화장품명 (명확한 경우)\\\",\\n"
            "  \\\"compatibility_score\\\": int(0-100),\\n"
            "  \\\"fusion_report\\\": {\\n"
            "    \\\"texture_match\\\": \\\"string\\\",\\n"
            "    \\\"ingredient_affinity\\\": \\\"string\\\",\\n"
            "    \\\"climate_suitability\\\": \\\"string\\\"\\n"
            "  },\\n"
            "  \\\"consult\\\": {\\n"
            "    \\\"summary\\\": \\\"string\\\",\\n"
            "    \\\"synergy_effects\\\": [\\\"string\\\"],\\n"
            "    \\\"precautions\\\": [\\\"string\\\"]\\n"
            "  },\\n"
            "  \\\"final_action\\\": {\\n"
            "    \\\"optimal_timing\\\": \\\"string\\\",\\n"
            "    \\\"usage_tip\\\": \\\"string\\\",\\n"
            "    \\\"risk_summary\\\": \\\"string\\\"\\n"
            "  },\\n"
            "  \\\"scores\\\": { \\\"total_health\\\": int, \\\"radiance\\\": int, \\\"vitality\\\": int, \\\"resilience\\\": int, \\\"climate_adaptability\\\": int }\\n"
            "}\\n"
        )

        # [FOOD ANALYSIS v1.0.0 - CLINICAL NUTRITION]
        self.food_instruction = (
            "귀하는 식품 섭취가 사용자의 피부 생체 리듬과 노화에 미치는 영향을 분석하는 '임상 영양 뷰티 가디언'입니다.\n"
            "**[v1.0.0-FOOD 분석 지침]**:\n"
            "1. **성분 기반 과학적 분석**: 사진 속 식품을 인식하고, 포함된 주요 성분이 피부 세포에 미치는 기전을 설명하십시오.\n"
            "2. **[중요] 모호성 배제**: 사진이 흐릿하거나 식품을 명확하게 식별할 수 없는 경우, 추측하거나 짐작하여 분석하지 마십시오. 이 경우 `consult.summary`에 '사진 화질이나 정보가 부족하여 명확한 분석이 불가능합니다'라고 명시하십시오.\n"
            "3. **개인 맞춤형 분석**: 사용자의 피부 타입, 연령, 기후 정보를 종합하여 섭취 시 실질적인 장단점을 과학적으로 기술하십시오.\n"
            "4. **피부 반응 예측**: 당화 반응(Glycation) 등 생화학적 반응을 근거로 기술하십시오.\n"
            "**[응답 형식]**: JSON 구조 엄수.\n"
            "{\n"
            "  \"version\": \"1.0.0-FOOD\",\n"
            "  \"image_type\": \"food\",\n"
            "  \"title\": \"식별된 식품명 (명확한 경우)\",\n"
            "  \"compatibility_score\": int(0-100),\n"
            "  \"fusion_report\": {\n"
            "    \"texture_match\": \"string\",\n"
            "    \"ingredient_affinity\": \"string\",\n"
            "    \"climate_suitability\": \"string\"\n"
            "  },\n"
            "  \"consult\": {\n"
            "    \"summary\": \"string\",\n"
            "    \"synergy_effects\": [\"string\"],\n"
            "    \"precautions\": [\"string\"]\n"
            "  },\n"
            "  \"final_action\": {\n"
            "    \"optimal_timing\": \"string\",\n"
            "    \"usage_tip\": \"string\",\n"
            "    \"risk_summary\": \"string\"\n"
            "  },\n"
            "  \"scores\": { \"total_health\": int, \"radiance\": int, \"vitality\": int, \"resilience\": int, \"climate_adaptability\": int }\n"
            "}\n"
        )

    def analyze_image(self, image_path: str, context: Dict[str, Any] = {}, analysis_type: str = "general") -> Dict[str, Any]:
        if not self.api_key:
             raise RuntimeError("Gemini API Key is missing. Mock mode is strictly disabled.")

        try:
            img = None
            if image_path and os.path.exists(image_path):
                # [v8.8.1] Ensure file is not empty and is a valid image
                if os.path.getsize(image_path) == 0:
                    raise ValueError(f"Image file is empty (0 bytes): {os.path.basename(image_path)}")
                
                try:
                    # [v8.8.2] Detect Encoding/Corruption early
                    with open(image_path, 'rb') as f:
                        header = f.read(20)
                        if header.startswith(b'---') or b'WebKitForm' in header:
                            raise ValueError("Data encoding error: Received multipart boundary indeed of raw binary image.")
                    
                    img = Image.open(image_path)
                    img.verify() # First pass verification
                    img = Image.open(image_path) # Re-open for actual use
                except Exception as img_err:
                    raise ValueError(f"Invalid or corrupted image format: {img_err}")
            else:
                # [v12.0.5] Support Image-less analysis (e.g. Cosmetic / Routine mode)
                print(f"[AI-Engine] Image-less request detected for {analysis_type}. Proceeding with text-only context.")
            
            location = context.get("location", "Unknown Location")
            weather = context.get("weather", "Unknown Weather")
            lifestyle = context.get("lifestyle", "Not provided")
            user_profile = context.get("user_profile", "Anonymous")
            
            # [v11.7.8] Truncate large profile data in console to prevent UnicodeEncodeError crash
            safe_profile_summary = str(user_profile)[:100] + "..." if len(str(user_profile)) > 100 else str(user_profile)
            print(f"[AI-Engine] Analyzing {analysis_type} for {location} (User: {safe_profile_summary})...")
            
            if analysis_type == "vanity":
                instruction = self.system_instruction
            elif analysis_type == "routine_consultation" or analysis_type == "routine":
                instruction = self.routine_consultation_instruction
            elif analysis_type == "product":
                instruction = self.product_instruction
            elif analysis_type == "cosmetic":
                instruction = self.cosmetic_instruction
            elif analysis_type == "food":
                instruction = self.food_instruction
            else:
                instruction = self.system_instruction
            
            # [v13.0.0] Bridge context for Delta-Tracking (Map engine key to prompt key)
            prev_analysis = context.get("previous_analysis") or context.get("skin_context")

            env_constraint = (
                f"- Analysis Mode: {analysis_type}\n"
                f"- Target Product: {context.get('target_product', 'Not specified')}\n"
                f"- Routine: {context.get('routine', 'Not provided')}\n"
                f"- Previous Analysis: {prev_analysis if prev_analysis else 'None provided (Focus on baseline analysis)'}\n"
                f"- Location: {location} (Climate: {weather})\n"
                f"- Preferred Language: {context.get('lang', 'en')}\n"
                f"\n[CRITICAL: COMPARATIVE ANALYSIS (Delta-Tracking)]\n"
                f"1. IF 'Previous Analysis' is provided, compare CURRENT biometrics/scores with the previous ones.\n"
                f"2. Explicitly mention the score changes in 'summary' and 'visual_progress' (e.g., 'Previous 78 -> Current 72').\n"
                f"3. Explain WHY the scores changed (e.g. climate impact, routine efficacy, or user's lifestyle causality).\n"
                f"4. If this is the FIRST scan (None provided), focus on establishing a strong baseline.\n"
                f"Analyze strictly based on the target product and user data provided above. NO HARDCODING."
            )
            
            contents = [instruction + env_constraint]
            if img:
                contents.append(img)
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.0
                )
            )
            
            if response and response.text:
                json_str = response.text.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
                
                json_dict = json.loads(json_str, strict=False)
                print(f"[AI-Engine] Analysis ({analysis_type}) Successful")
                self._save_to_logs(json_dict, analysis_type=analysis_type)
                return json_dict
            else:
                raise ValueError("Empty response from AI")
            
        except Exception as e:
            print(f"[AI-Engine] Analysis failed: {e}")
            raise e

    def _save_to_logs(self, data: Dict[str, Any], is_mock: bool = False, analysis_type: str = "general"):
        """Saves raw JSON result to files."""
        try:
            safe_type = "vanity" if analysis_type == "vanity" else "general"
            log_dir = Path("logs/analysis_results") / safe_type
            log_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "raw_fail_" if is_mock else "raw_result_"
            filename = f"{prefix}{timestamp}.json"
            filepath = log_dir / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"[SUCCESS] Raw {safe_type} AI result saved to: {filepath}")
        except Exception as e:
            print(f"[FAILURE] Failed to save raw log: {e}")

    def analyze_product(self, image_path: str, product_type: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Proxy for product analysis using analyze_image logic."""
        return self.analyze_image(image_path, context, analysis_type="product")

if __name__ == "__main__":
    print("[AI-Engine] GuardianVisionEngine Loaded. (Mock mode: DISABLED)")
    # No more mock calls.
