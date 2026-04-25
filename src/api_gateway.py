from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import uuid
import json
import datetime
import io
import dataclasses

# [v10.6.8] Load environment variables early with override
load_dotenv(override=True)

# [v10.6.7] Force UTF-8 for Windows Console to prevent Encoding Errors with Emojis
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# [v15.4.1] Debug API Key Loading (Masked)
_key = os.getenv("GEMINI_API_KEY", "")
_masked = f"{_key[:5]}...{_key[-5:]}" if len(_key) > 10 else "MISSING"
print(f"🔑 [System-Init] Loaded API Key: {_masked}")

# Add project root to path for package recognition
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.engine import TotalBeautyGuardianEngine

# Setup absolute paths for static files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'web')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
CORS(app)

# 🛡️ 하네스 규칙: 의학 용어 필터링 (VERISKIN_HARNESS.md Rule 2)
def filter_medical_terms(data):
    """
    JSON 데이터 내의 모든 문자열을 재귀적으로 검색하여 금지어를 순화어로 치환
    """
    replacements = {
        "치료": "개선",
        "진단": "분석",
        "처방": "가이드",
        "의사": "전문가",
        "매우": "상황에 따른", # 정성적 표현 조절
        "수술": "케어",
        "질환": "상태"
    }
    
    if isinstance(data, dict):
        return {k: filter_medical_terms(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [filter_medical_terms(v) for v in data]
    elif isinstance(data, str):
        for old, new in replacements.items():
            data = data.replace(old, new)
        return data
    return data

# Serve the main UI
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Initialize the Guardian Engine
guardian = TotalBeautyGuardianEngine()

BASE_PROJECT_DIR = os.path.dirname(BASE_DIR)
UPLOAD_FOLDER = os.path.join(BASE_PROJECT_DIR, 'data', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# [v10.6.5] Mode-based Log Folders for Engine
LOG_DIR = os.path.join(BASE_PROJECT_DIR, 'logs')
ANALYSIS_MODES = ['face', 'skin', 'routine', 'cosmetic', 'food']
for mode in ANALYSIS_MODES:
    os.makedirs(os.path.join(LOG_DIR, mode), exist_ok=True)

def get_mapped_mode(analysis_type):
    """표준 분석 모드(face, skin, routine)로 매핑"""
    mapping = {
        'face': 'face', 'general': 'face',
        'skin': 'skin', 'vanity': 'skin',
        'routine': 'routine', 'routine_consultation': 'routine',
        'cosmetic': 'cosmetic',
        'food': 'food'
    }
    return mapping.get(analysis_type, 'face')

def save_engine_log(mode, filename, data):
    """엔진 레이어의 분석 로그 저장 (폴더 자동 생성 포함)"""
    try:
        mapped_mode = get_mapped_mode(mode)
        target_dir = os.path.join(LOG_DIR, mapped_mode)
        
        # [v15.3.10] Ensure subfolder exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            
        path = os.path.join(target_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"📤 [Engine-Log] Saved {filename} to logs/{mapped_mode}/")
    except Exception as e:
        print(f"⚠️ [Log-Error] Failed to save engine log: {e}")

import traceback

# [v12.1.0] Ultra-Safe JSON Parser to prevent 500 errors before analysis
def safe_json_loads(val, default_val={}):
    if not val:
        return default_val
    if isinstance(val, (dict, list)):
        return val
    try:
        if isinstance(val, str) and (val.startswith('{') or val.startswith('[')):
            return json.loads(val)
        return default_val
    except:
        return default_val

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    # CORS 사전 검사(OPTIONS) 대응
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        # [STEP 1] Data Ingress - Essential Data Extraction
        if request.is_json or request.mimetype == 'application/json':
            data = request.get_json(force=True, silent=True) or {}
        else:
            data = request.form
        
        print(f"[STEP 1] Raw data extraction completed. (Mode: {data.get('mode') or data.get('analysis_type')})")
        
        # [v12.0.1] Input Harmonization (analysis_type vs mode)
        # [DEBUG] Changed default to DEBUG_GENERAL to verify deployment
        analysis_type = data.get('mode') or data.get('analysis_type') or 'DEBUG_GENERAL'
        print(f"\n" + "!" * 40)
        print(f"[NEW REQUEST] Analysis Mode Detected: {analysis_type.upper()}")
        print(f"!" * 40 + "\n")
        
        # [MOD] routine 및 cosmetic 분석은 이미지가 필수가 아님
        if 'image' not in request.files and analysis_type not in ['routine_consultation', 'routine', 'cosmetic']:
            if not (request.is_json and data.get('image_url')):
                 print("[DEBUG] Image missing for non-exempt mode.")
                 return jsonify({"error": f"No image uploaded for {analysis_type} analysis"}), 400
            
        file = request.files.get('image')
        user_id = data.get('user_id', 'Unknown')
        location = data.get('location', 'Seoul, Korea')
        weather = data.get('weather', 'Clear (Standard)')
        
        # [v12.1.0] Apply Safe Parsers
        routine = safe_json_loads(data.get('routine'), [])
        product_type = data.get('product_type') or ( 'food' if analysis_type == 'food' else 'cosmetic' if analysis_type == 'cosmetic' else 'face' )
        reg_data = safe_json_loads(data.get('registration_data') or data.get('registration'))
        lifestyle = data.get('lifestyle', 'Balanced')
        camera = safe_json_loads(data.get('camera'))
        lang = data.get('lang') or request.accept_languages.best or 'en'
        
        skin_context = safe_json_loads(data.get('skin_context') or data.get('previous_analysis'))
        metadata = safe_json_loads(data.get('metadata_json'))
        
        print(f"[STEP 2] Synthesis: Data normalization done. (User: {user_id})")
        
        print(f"[STEP 2] Synthesis: Data normalization done. (User: {user_id}, Mode: {analysis_type})")

        # Override individual fields with rich metadata if available
        if metadata.get("registration_data"):
             reg_data = metadata["registration_data"]
        if metadata.get("routine"):
             routine = metadata["routine"]
        if metadata.get("camera"):
             camera = metadata["camera"]
        if metadata.get("weather"):
             weather = metadata["weather"]
        if metadata.get("skin_context") or metadata.get("previous_analysis"):
             # [NEW] Prioritize historical/baseline scores from client metadata
             skin_context = metadata.get("skin_context") or metadata.get("previous_analysis")
        
        # ────────────────────────────────────────────────
        # 🧪 [GATEWAY-TRACE] Final Context Check
        # ────────────────────────────────────────────────
        print(f"\n>>>> [TRACE-IN] User: {user_id} | Mode: {analysis_type}")
        print(f"     - Image File: {file.filename if file else 'NONE'}")
        print(f"     - Reg Data Keys: {list(reg_data.keys()) if isinstance(reg_data, dict) else 'NOT_A_DICT'}")
        print(f"     - Routine Sample: {str(routine)[:50]}...")
        print(f"     - Metadata Logic: {'Enriched' if metadata else 'Standard'}")
        print("<<<< [TRACE-END]\n")
        
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # [v8.9.0] Robust Save & Sync
        if file:
            file.save(filepath)
            with open(filepath, 'ab') as f:
                os.fsync(f.fileno()) # Force write to physical storage
        else:
            filepath = None
            
        print(f"[Server] Starting Engine Analysis (Mode: {product_type}, Type: {analysis_type})...")
        
        # [v13.5.1] Redundant block removed. Analysis is now handled by the central dispatcher below.
        # [v10.6.5] 📂 엔진 수신 데이터 로그 기록 (req_*.json)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        req_filename = f"req_{timestamp}.json"
        engine_req_data = {
            "analysis_type": analysis_type,
            "product_type": product_type,
            "location": location,
            "weather": weather,
            "lang": lang,
            "registration_data": reg_data,
            "lifestyle": lifestyle,
            "routine": routine
        }
        print(f"[STEP 3] Engine Ingress: Preparing payload for {analysis_type}...")
        mapped_mode = get_mapped_mode(analysis_type)
        save_engine_log(mapped_mode, req_filename, engine_req_data)
        print(f"[Server] Request log saved to logs/{mapped_mode}/{req_filename}")

        # [v13.5.0] [Central Dispatcher]
        if analysis_type == 'skin' or analysis_type == 'vanity':
            print(f"[Server] Starting Skin Analysis (v1.2.0-SKIN-PRO)...")
            report_json = guardian.analyze_vanity(
                image_path=filepath,
                location=location,
                registration_data=reg_data,
                weather_context=weather,
                lifestyle_24h=lifestyle,
                camera_metadata=camera,
                current_routine=routine,
                lang=lang,
                skin_context=skin_context
            )
        elif analysis_type == 'routine' or analysis_type == 'routine_consultation':
            print(f"[Server] Starting Routine consultation Analysis...")
            report_json = guardian.analyze_routine_consultation(
                routine=routine,
                skin_context=skin_context,
                location=location,
                registration_data=reg_data,
                weather_context=weather,
                camera_metadata=camera,
                lang=lang
            )
        elif analysis_type == 'cosmetic' or analysis_type == 'food':
            print(f"[Server] Starting {analysis_type.upper()} Analysis...")
            p_name = data.get('product_name') or data.get('item_name')
            target_prod = p_name if (p_name and str(p_name).lower() != 'null') else "Target Item"
            
            report_json = guardian.analyze_product(
                image_path=filepath, 
                product_type=analysis_type,
                location=location,
                registration_data=reg_data,
                weather_context=weather,
                lifestyle_24h=lifestyle,
                lang=lang,
                skin_context=skin_context
            )
        elif analysis_type == 'face' or analysis_type == 'general':
            print(f"[Server] Starting Face Analysis (v3.1.7-FACE-PRO)...")
            report_json = guardian.analyze_image(
                image_path=filepath,
                location=location,
                registration_data=reg_data,
                weather_context=weather,
                lifestyle_24h=lifestyle,
                camera_metadata=camera,
                current_routine=routine,
                lang=lang,
                skin_context=skin_context,
                analysis_type="vanity"
            )
        else:
             print(f"[Server] Unknown analysis type '{analysis_type}'. Falling back to Face Mode.")
             report_json = guardian.analyze_image(image_path=filepath, location=location, lang=lang)

        # [Harness] Immediate destruction after analysis (Rule 1)
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print(f"[Harness] {filename} original image deleted.")
        
        print(f"[Server] Analysis Successful & Filtered")
        
        # [Harness] Refine and filter analysis results
        # [v10.6.9] Convert dataclass object to dictionary for robust filtering/logging
        if hasattr(report_json, "__dataclass_fields__"):
             filtered_data = dataclasses.asdict(report_json)
        else:
             filtered_data = report_json.copy() if isinstance(report_json, dict) else report_json
        
        # [v10.6.9-FIX] Ensure image_type matches the intended analysis mode
        # If the engine result doesn't explicitly flag it, use the mapped analysis mode
        image_type = filtered_data.get("image_type")
        if not image_type or image_type == "face":
             if mapped_mode == "routine":
                 image_type = "routine"
             else:
                 image_type = filtered_data.get("image_type", product_type)
        
        filtered_data["image_type"] = image_type
        
        if image_type != "face":
            print(f"[Harness] {image_type} analysis mode: skipping biometrics filtering")
        
        # 2. 신뢰도 지표(confidence_metrics) 추가
        real_conf = filtered_data.get('biometrics', {}).get('confidence_score', 85)
        filtered_data['confidence_metrics'] = {
            "score": round(real_conf / 100.0, 2), # 0-100 scale to 0.0-1.0
            "lighting": "Critical" if real_conf < 40 else ("Fair" if real_conf < 70 else "Good"),
            "blur": "Detected" if real_conf < 50 else "None",
            "message": "현재 조명 및 초점 상태가 안정적입니다." if real_conf >= 40 else "촬영 환경이 분석에 적합하지 않습니다."
        }

        # ────────────────────────────────────────────────
        # 📋 [CLIENT RESPONSE LOG] 클라이언트 리턴값 확인
        # ────────────────────────────────────────────────
        consult = filtered_data.get("consult", {})
        summary_text  = consult.get("summary",  "(None)")
        skincare_text = consult.get("skincare", "(None)")
        makeup_text   = consult.get("makeup",   "(None)")
        hair_text     = consult.get("hair",     "(None)")

        LIMITS = {"summary": 200, "skincare": 150, "makeup": 150, "hair": 100}
        fields = {
            "summary ": (summary_text,  LIMITS["summary"]),
            "skincare": (skincare_text, LIMITS["skincare"]),
            "makeup  ": (makeup_text,   LIMITS["makeup"]),
            "hair    ": (hair_text,     LIMITS["hair"]),
        }
        print("\n" + "=" * 64)
        print(f"[CLIENT RESPONSE] {image_type.upper()} Analysis Result Preview")
        print("=" * 64)
        
        if image_type == "face":
            for label, (text, min_len) in fields.items():
                content = text if text else "(None)"
                status = "PASS" if len(content) >= min_len else f"FAIL (Min: {min_len} chars)"
                print(f"{label}  {len(content)} chars  {status}")
                print(f"   {content[:100]}{'...' if len(content) > 100 else ''}")
                print()
            
            # [PRO 3.1.7] Final Action for Face
            action = filtered_data.get("final_action", {})
            tip = action.get('professional_tip') or "(None)"
            print(f"[5. Action] {action.get('risk_summary') or '(None)'}")
            print(f"   Tip: {tip[:100]}...")
        else:
            # [NEW] Product/Food Analysis Logging (v3.1.7-PRO)
            prod = filtered_data.get("product_analysis", {})
            match = filtered_data.get("skin_matching", {})
            dossier = filtered_data.get("dossier", {})
            risks = filtered_data.get("risks", {})
            action = filtered_data.get("final_action", {})
            
            print(f"[1. Product] {prod.get('item_name')} | {prod.get('brand_name')} ({prod.get('category')})")
            match_reason = match.get('match_reason') or "(None)"
            medical_report = dossier.get('medical_report') or "(None)"
            conflict_report = risks.get('conflict_report') or "(None)"
            prof_tip = action.get('professional_tip') or "(None)"
            
            print(f"[2. Matching] {match.get('compatibility_score')} | {match_reason[:60]}...")
            print(f"[3. Dossier] {medical_report[:80]}...")
            print(f"[4. Risks] {conflict_report[:80]}...")
            print(f"[5. Action] {prof_tip[:80]}...")
            
        print("=" * 64 + "\n")
        # ------------------------------------------------

        # [v3.0.0] Final safety harness: purification of medical terms
        final_safe_data = filter_medical_terms(filtered_data)
        
        # [v10.6.5] Engine Result Data Logging (res_*.json)
        try:
            res_filename = f"res_{timestamp}.json" # 요청 시와 동일한 타임스탬프 사용
            save_engine_log(mapped_mode, res_filename, final_safe_data)
            print(f"[Server] Response log saved to logs/{mapped_mode}/{res_filename}")
        except Exception as res_log_e:
            print(f"[Server] Failed to save response log: {res_log_e}")
            
        # [v11.0.1] Print full JSON response as requested by USER
        print("\n" + "--- [FINAL RESPONSE JSON] ---")
        try:
             print(json.dumps(final_safe_data, indent=4, ensure_ascii=False))
        except:
             print("[Server] Result too large to print fully or encoding conflict.")
        print("--- [END OF RESPONSE] ---\n")

        return jsonify(final_safe_data)
        
    except Exception as e:
        print("\n" + "!"*50)
        print(f"[Server Critical Error] {str(e)}")
        import traceback
        tb = traceback.format_exc()
        try:
            # Force ASCII to ensure output in Windows terminal
            print(tb.encode('ascii', 'ignore').decode('ascii'))
        except:
            print(f"Server Exception: {e}")
        
        # Save traceback to a local file for investigation [TEMPORARY DEBUG]
        try:
            with open("debug_error.log", "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.datetime.now()}] Error: {str(e)}\n")
                f.write(tb)
                f.write("\n" + "="*50 + "\n")
        except:
            pass
            
        print("!"*50 + "\n")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "="*50)
    print("VeriSkin Guardian v2.2 Server starting...")
    print("UI Access: http://localhost:8000")
    print("API Endpoint: http://localhost:8000/analyze")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=8000, debug=True)
