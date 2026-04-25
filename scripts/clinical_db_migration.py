import psycopg2
import re
import os

# DB Connection params
DB_PARAMS = {
    "host": "72.62.254.119",
    "user": "verisadmin",
    "password": "veris1234!",
    "dbname": "veriskin"
}

RAW_REPORT_PATH = r"d:\Workspace\SkinEngine\knowledge\AI 스킨케어 분석용 정밀 데이터베이스 설계 리포트.md"

def extract_cells_from_raw(content):
    # 1. Pre-clean: Remove escapes and bold markers
    content = content.replace(r"\.", ".").replace(r"\_", "_").replace(r"\|", "|").replace(r"\-", "-").replace(r"\*", "")
    content = content.replace("**", "").replace("__", "")
    
    # 2. Extract all cells by splitting by |
    # This ignores newlines, treat the whole file as a stream of cells
    raw_cells = [c.strip() for c in content.split("|")]
    
    # Filter out cells that are just whitespace or markdown artifacts like ":---"
    cells = []
    for c in raw_cells:
        if not c: continue
        if re.match(r"^[:\s\-]+$", c): continue
        cells.append(c)
        
    return cells

def migrate_clinical_data():
    if not os.path.exists(RAW_REPORT_PATH):
        print(f"[Error] File not found: {RAW_REPORT_PATH}")
        return

    with open(RAW_REPORT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    cells = extract_cells_from_raw(content)
    
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Pointer to current cell in the stream
    p = 0
    total_cells = len(cells)
    
    while p < total_cells:
        cell = cells[p]
        
        # 1. Disease Guidelines (Expect 8 columns)
        # Sequence: D001, Name, Patho, Source, Rx, Cleansing, Moist, Contra
        if re.match(r"^D\d{3}", cell):
            if p + 7 < total_cells:
                row = cells[p:p+8]
                print(f"[*] Found Disease: {row[0]} - {row[1]}")
                cur.execute("""
                    INSERT INTO SE_disease_official_guidelines 
                    (disease_id, disease_name, pathophysiology, guideline_source, core_medical_rx, cleansing_guide, moisturizing_guide, contraindications)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (disease_id) DO UPDATE SET 
                        disease_name = EXCLUDED.disease_name, pathophysiology = EXCLUDED.pathophysiology,
                        guideline_source = EXCLUDED.guideline_source, core_medical_rx = EXCLUDED.core_medical_rx,
                        cleansing_guide = EXCLUDED.cleansing_guide, moisturizing_guide = EXCLUDED.moisturizing_guide, 
                        contraindications = EXCLUDED.contraindications;
                """, tuple(row))
                p += 8
                continue
        
        # 2. Symptom Mapping (Expect 5 columns)
        # Sequence: S001, Symptom, Hero, Villain, Evidence
        if re.match(r"^S\d{3}", cell):
            if p + 4 < total_cells:
                row = cells[p:p+5]
                print(f"[*] Found Symptom: {row[0]} - {row[1][:20]}...")
                
                # Risk level logic from Villain column
                risk_level = 0
                if "등급 3~5" in row[3]: risk_level = 4
                
                cur.execute("""
                    INSERT INTO SE_symptom_ingredient_mapping 
                    (symp_id, clinical_symptoms, hero_ingredients, villain_ingredients, comedogenic_risk_level, clinical_evidence)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symp_id) DO UPDATE SET 
                        clinical_symptoms = EXCLUDED.clinical_symptoms, hero_ingredients = EXCLUDED.hero_ingredients,
                        villain_ingredients = EXCLUDED.villain_ingredients, comedogenic_risk_level = EXCLUDED.comedogenic_risk_level,
                        clinical_evidence = EXCLUDED.clinical_evidence;
                """, (row[0], row[1], row[2], row[3], risk_level, row[4]))
                p += 5
                continue

        # 3. MFDS Regulations (Expect 6 columns)
        # Sequence: R001, Category, Name, Limit, Efficacy, Warning
        if re.match(r"^R\d{3}", cell):
            if p + 5 < total_cells:
                row = cells[p:p+6]
                print(f"[*] Found Regulation: {row[0]} - {row[1]}")
                cur.execute("""
                    INSERT INTO SE_mfds_ingredient_regulation 
                    (reg_id, functional_category, inci_name, concentration_limit, efficacy_claim_rule, legal_warning_memo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (reg_id) DO UPDATE SET 
                        functional_category = EXCLUDED.functional_category, inci_name = EXCLUDED.inci_name,
                        concentration_limit = EXCLUDED.concentration_limit, efficacy_claim_rule = EXCLUDED.efficacy_claim_rule,
                        legal_warning_memo = EXCLUDED.legal_warning_memo;
                """, tuple(row))
                p += 6
                continue
        
        p += 1 # Move to next cell if no match

    conn.commit()
    cur.close()
    conn.close()
    print("[Success] Clinical intelligence migration completed.")

if __name__ == "__main__":
    migrate_clinical_data()
