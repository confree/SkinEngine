from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import uuid
import json
import datetime
import io
import dataclasses

# [v10.6.7] Force UTF-8 for Windows Console to prevent Encoding Errors with Emojis
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

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
ANALYSIS_MODES = ['face', 'skin', 'routine']
for mode in ANALYSIS_MODES:
    os.makedirs(os.path.join(LOG_DIR, mode), exist_ok=True)

def get_mapped_mode(analysis_type):
    """표준 분석 모드(face, skin, routine)로 매핑"""
    mapping = {
        'face': 'face', 'general': 'face',
        'skin': 'skin', 'vanity': 'skin',
        'routine': 'routine', 'routine_consultation': 'routine'
    }
    return mapping.get(analysis_type, 'face')

def save_engine_log(mode, filename, data):
    """엔진 레이어의 분석 로그 저장"""
    try:
        mapped_mode = get_mapped_mode(mode)
        path = os.path.join(LOG_DIR, mapped_mode, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Log-Error] Failed to save engine log: {e}")

import traceback

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    # CORS 사전 검사(OPTIONS) 대응
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    try:
        # [NEW LOG] 요청 인지 즉시 출력
        analysis_type = request.form.get('analysis_type', 'general')
        print(f"\n[NEW REQUEST] Analysis Mode: {analysis_type.upper()}")
        
        
        # [MOD] routine_consultation은 이미지가 필수가 아님
        if 'image' not in request.files and analysis_type not in ['routine_consultation', 'routine']:
            return jsonify({"error": f"No image uploaded for {analysis_type} analysis"}), 400
            
        file = request.files.get('image')
        location = request.form.get('location', 'Seoul, Korea')
        weather = request.form.get('weather', 'Clear (Standard)')
        routine = request.form.get('routine', '[]')
        product_type = request.form.get('product_type', 'face') # NEW: face | food | cosmetic
        analysis_type = request.form.get('analysis_type', 'general') # [NEW] vanity | general
        
        # [NEW] Multi-modal Data Parsing
        reg_data = request.form.get('registration_data', '{}')
        lifestyle = request.form.get('lifestyle', 'Balanced')
        camera = request.form.get('camera', '{}')
        lang = request.form.get('lang', 'ko-KR')
        
        # [v10.7.2] Intelligence Metadata Parsing (Priority Context)
        metadata_raw = request.form.get('metadata_json', '{}')
        metadata = json.loads(metadata_raw)
        
        # Initialize skin_context (for routine consultation)
        skin_context_raw = request.form.get('skin_context', '{}')
        skin_context = json.loads(skin_context_raw)

        # Override individual fields with rich metadata if available
        if metadata.get("registration_data"):
             reg_data = json.dumps(metadata["registration_data"])
        if metadata.get("routine"):
             routine = json.dumps(metadata["routine"])
        if metadata.get("camera"):
             camera = json.dumps(metadata["camera"])
        if metadata.get("weather"):
             weather = metadata["weather"]
        if metadata.get("skin_context"):
             # [NEW] Prioritize historical/baseline scores from client metadata
             skin_context = metadata["skin_context"]
        
        # ────────────────────────────────────────────────
        # 📥 [CLIENT REQUEST LOG] 클라이언트 수신 데이터 확인
        # ────────────────────────────────────────────────
        print("\n" + "=" * 64)
        print(f"[CLIENT REQUEST] {product_type.upper()} ({analysis_type}) Analysis received")
        print("=" * 64)
        print(f"Image     : {file.filename if file else 'N/A'}")
        print(f"Intelligence Source: {'Enriched Metadata' if metadata_raw != '{}' else 'Individual Fields'}")
        print(f"Registration: {reg_data}")
        print(f"Intelligence Metadata: {metadata_raw[:200]}...") # Log partial for safety
        print("=" * 64 + "\n")
        
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
        
        if product_type in ['food', 'cosmetic']:
            # ... (기존 product logic)
            analysis_result = guardian.analyze_product(
                image_path=filepath if 'file' in locals() else None, # filepath exists if file was saved
                product_type=product_type,
                location=location,
                registration_data=json.loads(reg_data),
                weather_context=weather,
                lifestyle_24h=lifestyle,
                lang=lang
            )
            report_json = analysis_result
        # [v10.6.5] 📂 엔진 수신 데이터 로그 기록 (req_*.json)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        req_filename = f"req_{timestamp}.json"
        engine_req_data = {
            "analysis_type": analysis_type,
            "product_type": product_type,
            "location": location,
            "weather": weather,
            "lang": lang,
            "registration_data": json.loads(reg_data),
            "lifestyle": lifestyle,
            "routine": json.loads(routine)
        }
        mapped_mode = get_mapped_mode(analysis_type)
        save_engine_log(mapped_mode, req_filename, engine_req_data)
        print(f"[Server] Request log saved to logs/{mapped_mode}/{req_filename}")

        # [v10.6.0] Unified Analysis Type Mapping
        if analysis_type == 'skin' or analysis_type == 'vanity':
             # ... (기존 skin 로직)
            # [NEW] Skin / Efficacy Tracking Mode
            print(f"[Server] Starting Skin Analysis (v1.2.0-SKIN-PRO)...")
            report_json = guardian.analyze_vanity(
                image_path=filepath,
                location=location,
                registration_data=json.loads(reg_data),
                weather_context=weather,
                lifestyle_24h=lifestyle,
                camera_metadata=json.loads(camera),
                current_routine=json.loads(routine),
                lang=lang
            )
        elif analysis_type == 'routine' or analysis_type == 'routine_consultation':
            # [NEW] Routine Consultation Logic
            print(f"[Server] Starting Routine consultation Analysis...")
            report_json = guardian.analyze_routine_consultation(
                routine=json.loads(routine),
                skin_context=skin_context,
                location=location,
                registration_data=json.loads(reg_data),
                weather_context=weather,
                camera_metadata=json.loads(camera),
                lang=lang
            )
        elif analysis_type == 'face' or analysis_type == 'general':
            # Full Skin/Face Analysis Mode
            print(f"[Server] Starting Face Analysis (v3.1.7-FACE-PRO)...")
            report_json = guardian.analyze_image(
                image_path=filepath,
                location=location,
                registration_data=json.loads(reg_data),
                weather_context=weather,
                lifestyle_24h=lifestyle,
                camera_metadata=json.loads(camera),
                current_routine=json.loads(routine),
                lang=lang,
            )
        else:
             # Default fallback
             print(f"[Server] Unknown analysis type '{analysis_type}'. Falling back to Face Mode.")
             report_json = guardian.analyze_image(image_path=filepath, lang=lang)

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
            
        return jsonify(final_safe_data)
        
    except Exception as e:
        print("\n" + "!"*50)
        print(f"[Server Critical Error] {str(e)}")
        import traceback
        tb = traceback.format_exc()
        try:
            print(tb)
        except:
            print("Could not print traceback due to encoding error")
        
        # Save traceback to a file for investigation
        try:
            with open("C:/Users/jaesu/.gemini/antigravity/brain/39f5faaa-0d06-4be8-ac3a-223983c0cb0e/scratch/error_traceback.txt", "w", encoding="utf-8") as f:
                f.write(tb)
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
