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

class GuardianVisionEngine:
    """
    [Guardian-Vision-v3.5]
    Kbeauty-Proven Architecture: SDK + Pillow + models/ Prefix.
    Restores real-time AI connectivity using the success pattern from 2 days ago.
    """
    
    def __init__(self, api_key: str = None):
        # [SECURITY] Mock Mode Strictly Disabled. API Key is MANDATORY.
        self.api_key = api_key or "AIzaSyD1MVFUZux4oHnk8hEimxgwFqKq7EaOENU"
        self.client = genai.Client(api_key=self.api_key)
        
        # [VERSION v4.0 - NEXT-GEN STABLE] 
        self.model_id = 'models/gemini-2.5-flash'
        print(f"[READY] [AI-Engine] VeriSkin Guardian Ready: Targeting {self.model_id}")
        
        # [SKIN ANALYSIS v3.1.7 - PRO LIVE]
        self.system_instruction = (
            "귀하는 사용자의 전인적 미(Beauty)를 완성하는 '스마트 뷰티 가디언'입니다.\n"
            "**[v3.1.7-PRO 피부 정밀 분석 지침]**:\n"
            "1. **생체 지표 (Biometrics)**: 나이, ITA(피부톤 수치), 타입, 탄력, 멜라닌/홍반 지수 등을 정밀 산출하십시오.\n"
            "2. **구조 분석 (Face Geometry)**: 얼굴형, 비율, 대칭성 및 스타일링 권장 사항을 분석하십시오.\n"
            "3. **색채 과학 (Personal Color)**: CIELAB 수치, 퍼스털 컬러 타입 및 권장 팔레트를 도출하십시오.\n"
            "4. **맞춤 큐레이션 (Curation)**: 현재 기후를 반영한 스킨/메이크업/헤어 처방을 제시하십시오.\n"
            "5. **전문가 조언 (Consult)**: 각 영역별 텍스트 중심의 요약 조언을 제공하십시오.\n"
            "6. **위험 필터 (Risks)**: 성분 충돌, 산화 위험, 블랙리스트 성분 등 실시간 위협 요소를 필터링하십시오.\n"
            "7. **심층 도시에 (Dossier)**: 300자 이상의 심층 텍스트 보고서, 메이크업 전략, 이너뷰티 권고를 포함하십시오.\n"
            "8. **최종 액션 플랜 (Final Action)**: 종합 리스크 요약, 전문가 팁, 그리고 3단계 오프셋 루틴을 처방하십시오.\n"
            "**[응답 형식]**: 반드시 아래 JSON 구조 그대로 응답하고, 코드블럭으로 감싸십시오.\n"
            "{\n"
            "  \"version\": \"3.1.7-PRO\",\n"
            "  \"image_type\": \"face\",\n"
            "  \"biometrics\": { \"skin_age\": int, \"ita\": float, \"skin_type\": \"string\", \"skin_hex\": \"string\", \"elasticity_score\": \"float(0.0-100.0)\", \"melanin_index\": \"float(0.0-100.0)\", \"erythema_index\": \"float(0.0-100.0)\", \"pore_density\": \"string\", \"wrinkle_score\": \"float(0.0-100.0)\", \"age_range\": \"string\", \"confidence_score\": int },\n"
            "  \"face\": { \"shape\": \"string\", \"length_width_ratio\": float, \"asymmetry\": \"string\", \"jaw_tension\": \"string\", \"styling_recommendations\": { \"hair\": \"string\", \"brows\": \"string\" } },\n"
            "  \"color\": { \"cielab\": { \"L\": float, \"a\": float, \"b\": float }, \"seasonal_type\": \"string\", \"undertone\": \"string\", \"recommended_palette\": [], \"eye_hair_match\": \"string\" },\n"
            "  \"curation\": { \"skincare_prescription\": \"string\", \"makeup_prescription\": \"string\", \"hair_prescription\": \"string\", \"climate_adjustment\": \"string\" },\n"
            "  \"consult\": { \"summary\": \"string\", \"skincare\": \"string\", \"makeup\": \"string\", \"hair\": \"string\" },\n"
            "  \"risks\": { \"alert_level\": \"string\", \"makeup_oxidation_risk\": \"string\", \"scalp_thermal_risk\": \"string\", \"conflict_report\": \"string\", \"blacklist_ingredients\": [] },\n"
            "  \"dossier\": { \"medical_report\": \"string(300자 이상)\", \"makeup_strategy\": \"string\", \"hair_architecture\": \"string\", \"visual_prompt\": \"string\", \"shampoo_prescription\": \"string\", \"nutritional_advice\": \"string\" },\n"
            "  \"final_action\": { \"risk_summary\": \"string\", \"professional_tip\": \"string\", \"offset_routine\": [] },\n"
            "  \"scores\": { \"total_health\": \"int(0-100)\", \"radiance\": \"int(0-100)\", \"climate_adaptability\": \"int(0-100)\", \"vitality\": \"int(0-100)\", \"resilience\": \"int(0-100)\" }\n"
            "}\n"
        )

        # [VANITY/EFFICACY ANALYSIS v1.2.0-VANITY-PRO]
        self.vanity_instruction = (
            "귀하는 사용자의 피부 변화를 정밀하게 추적하고 제품의 효능을 입증하는 '임상 뷰티 가디언'입니다.\n"
            "**[v1.2.0-VANITY-PRO 루틴 효능 분석 지침]**:\n"
            "1. **미세 변화 감지**: 이전 상태와 비교하여 탄력, 주름, 멜라닌 지수의 미세한 변화(1~2% 내외)를 포착하여 수치화하십시오.\n"
            "2. **인과 관계 추론 (Causality)**: 루틴 성분, `previous_advice`(이전 조언), 그리고 생활 방식(수면, 음수)의 조화가 현재 피부 변화에 어떤 영향을 주었는지 '인과 관계' 중심으로 서술하십시오.\n"
            "3. **효능 입증 (Efficacy Proof)**: `skin_context`의 수치 변화와 시각적 변화가 일치하는지 검증하고, 현재 루틴의 효능을 궁합 점수로 환산하십시오.\n"
            "4. **미래 예측 및 사회적 증명**: 개선 속도를 바탕으로 미래의 마일스톤 예측과 대조 데이터를 제시하십시오.\n"
            "**[응답 형식]**: 아래 JSON 구조를 엄수하여 코드블럭으로 응답하십시오.\n"
            "{\n"
            "  \"analysis_id\": \"UUID-V10-SYNC\",\n"
            "  \"compatibility_score\": int,\n"
            "  \"version\": \"1.2.0-VANITY-PRO\",\n"
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
            "**[응답 형식]**: JSON 구조 엄수.\n"
            "{\n"
            "  \"version\": \"3.1.8-PRO\",\n"
            "  \"image_type\": \"cosmetic|food\",\n"
            "  \"product_analysis\": { \"item_name\": \"string\", \"key_ingredients\": [], \"brand_name\": \"string\", \"category\": \"string\" },\n"
            "  \"skin_matching\": { \"compatibility_score\": int, \"climate_clash\": \"string\", \"match_reason\": \"string\", \"warning_ingredients\": [] },\n"
            "  \"dossier\": { \"medical_report\": \"string\", \"nutritional_advice\": \"string\" },\n"
            "  \"risks\": { \"conflict_report\": \"string\", \"makeup_oxidation_risk\": \"string\", \"blacklist\": [], \"scalp_caution\": \"string\" },\n"
            "  \"final_action\": { \"risk_summary\": \"string\", \"professional_tip\": \"string\", \"offset_routine\": [] }\n"
            "}\n"
        )

        # [ROUTINE CONSULTATION v1.0.0]
        self.routine_consultation_instruction = (
            "귀하는 리얼타임 루틴 진단 전문가 '스마트 루틴 가디언'입니다.\n"
            "**[응답 형식]**: JSON 구조 엄수.\n"
            "{\n"
            "  \"version\": \"1.0.0\",\n"
            "  \"image_type\": \"routine\",\n"
            "  \"compatibility_score\": int,\n"
            "  \"consult\": {\n"
            "    \"summary\": \"string\",\n"
            "    \"skincare\": \"string\",\n"
            "    \"efficacy\": [{ \"target\": \"string\", \"reason\": \"string\" }],\n"
            "    \"conflicts\": [{ \"item_a\": \"string\", \"item_b\": \"string\", \"warning\": \"string\" }]\n"
            "  },\n"
            "  \"final_action\": { \"offset_routine\": [], \"professional_tip\": \"string\", \"risk_summary\": \"string\" },\n"
            "  \"scores\": { \"total_health\": int, \"radiance\": int, \"vitality\": int, \"resilience\": int, \"climate_adaptability\": int }\n"
            "}\n"
            "**주의**: image_type은 반드시 \"routine\"으로 고정하십시오."
        )

        # [COSMETIC HARMONIZATION v1.0.0]
        self.cosmetic_instruction = (
            "귀하는 사용자의 현재 피부 상태와 화장품 사이의 화합(Harmony)을 정밀 분석하는 '뷰티 융합 전문가'입니다.\\n"
            "**[v1.0.0-COSMETIC-PRO 분석 지침]**:\\n"
            "1. **조밀도 및 융합 분석**: 선택된 제품이 사용자 피부 타입 및 현재 컨디션(수분도, 유분도 등)에 얼마나 잘 융합될지 분석하십시오.\\n"
            "2. **성분-피부 궁합**: 특정 성분이 사용자의 피부 고민(트러블, 건조 등)에 미칠 긍정적/부정적 영향을 도출하십시오.\\n"
            "3. **리얼타임 기후 최적화**: 현재 위치와 날씨 정보를 바탕으로, 해당 화장품을 사용하기에 가장 적합한 시간대나 방법을 제안하십시오.\\n"
            "4. **시너지 및 충돌 리포트**: 기존 사용 중인 루틴 제품과의 성분 충돌 가능성이나 기대되는 시너지를 요약하십시오.\\n"
            "**[응답 형식]**: 반드시 아래 JSON 구조 그대로 응답하고, 코드블럭으로 감싸십시오.\\n"
            "{\\n"
            "  \\\"version\\\": \\\"1.0.0-COSMETIC\\\",\\n"
            "  \\\"image_type\\\": \\\"cosmetic\\\",\\n"
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
                            raise ValueError("Data encoding error: Received multipart boundary indeed of raw binary image. Please check gateway forwarding.")
                    
                    img = Image.open(image_path)
                    img.verify() # First pass verification
                    img = Image.open(image_path) # Re-open for actual use
                except Exception as img_err:
                    raise ValueError(f"Invalid or corrupted image format: {img_err}")
            
            location = context.get("location", "Unknown Location")
            weather = context.get("weather", "Unknown Weather")
            lifestyle = context.get("lifestyle", "Not provided")
            user_profile = context.get("user_profile", "Anonymous")
            
            print(f"📡 [AI-Engine] Analyzing {analysis_type} for {location} (User: {user_profile})...")
            
            if analysis_type == "vanity":
                instruction = self.vanity_instruction
            elif analysis_type == "routine_consultation" or analysis_type == "routine":
                instruction = self.routine_consultation_instruction
            elif analysis_type == "product":
                instruction = self.product_instruction
            elif analysis_type == "cosmetic":
                instruction = self.cosmetic_instruction
            else:
                instruction = self.system_instruction
            
            env_constraint = (
                f"- Analysis Mode: {analysis_type}\n"
                f"- Routine: {context.get('routine', 'Not provided')}\n"
                f"- Skin Context: {context.get('skin_context', 'Not provided')}\n"
                f"- Location: {location} (Climate: {weather})\n"
                f"- Preferred Language: {context.get('lang', 'ko-KR')}\n"
                f"Analyze strictly based on data. NO HARDCODING."
            )
            
            contents = [instruction + env_constraint]
            if img:
                contents.append(img)
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=contents
            )
            
            if response and response.text:
                json_str = response.text.strip()
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()
                
                json_dict = json.loads(json_str, strict=False)
                print(f"✅ [AI-Engine] Analysis ({analysis_type}) Successful")
                self._save_to_logs(json_dict, analysis_type=analysis_type)
                return json_dict
            else:
                raise ValueError("Empty response from AI")
            
        except Exception as e:
            print(f"❌ [AI-Engine] Analysis failed: {e}")
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
