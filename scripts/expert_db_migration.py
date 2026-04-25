import psycopg2
import os
import re
import json

def migrate_local_knowledge():
    conn_params = {
        "host": "72.62.254.119",
        "user": "verisadmin",
        "password": "veris1234!",
        "dbname": "veriskin"
    }
    
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    base_path = r"D:\Workspace\SkinEngine"
    knowledge_path = os.path.join(base_path, "knowledge")
    
    tables = ["SE_knowledge_base", "SE_safety_guards", "SE_products", "SE_routines", "SE_expert_channels"]
    for table in tables:
        cur.execute(f"DELETE FROM {table}")
    
    # --- 1. rules.md ---
    rules_path = os.path.join(base_path, "rules.md")
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            content = f.read()
        cur.execute("INSERT INTO SE_knowledge_base (category, title, content) VALUES (%s, %s, %s)",
                    ("Constitution", "VeriSkin Global AI K-Beauty Master Guide", content))
        
        matches = re.findall(r"#### (\d+\..*?)\n(.*?)(?=####|---|$|##)", content, re.DOTALL)
        for title, desc in matches:
            if any(x in title for x in ["BIPOC", "고온다습", "건조", "한랭"]):
                prohibited = re.findall(r"- \*\*절대 금기 조합\*\*: (.*?)\n", desc)
                cur.execute("INSERT INTO SE_safety_guards (target_group, prohibited_items, risk_description) VALUES (%s, %s, %s)",
                            (title.strip(), prohibited, desc.strip()))

    # --- 2. Protocols (Routines) ---
    protocol_file = "맞춤형 K-뷰티 스킨케어 프로토콜 가이드 4종.md"
    protocol_path = os.path.join(knowledge_path, protocol_file)
    if os.path.exists(protocol_path):
        with open(protocol_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Flexibly match ### 1\. or ### 1.
        routines = re.findall(r"### \d+.*?\.?\s*(.*?)\n(.*?)(?=###|$)", content, re.DOTALL)
        for name, desc in routines:
            # Match * **1단계: ...** or * **1단계:...**
            steps_matches = re.findall(r"\* \*\*(\d+단계:.*?)\s*.*?\*\*\s*(.*?)(?=\n\*|$)", desc)
            steps_data = [{"step": s[0].strip(), "description": s[1].strip()} for s in steps_matches]
            cur.execute("INSERT INTO SE_routines (name, description, steps) VALUES (%s, %s, %s)",
                        (name.strip(), desc.strip(), json.dumps(steps_data, ensure_ascii=False)))

    # --- 3. Expert Products ---
    product_file = "피부 고민별 맞춤 화장품 전문가 추천 가이드.md"
    product_path = os.path.join(knowledge_path, product_file)
    if os.path.exists(product_path):
        with open(product_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Match **1\. Brand - Product** or **1. Brand - Product**
        items = re.findall(r"\*\*\d+.*?\.?\s*(.*?)\s*\*\*\n\n(.*?)(?=\*\*|$)", content, re.DOTALL)
        for title_text, body in items:
            title_text = title_text.replace("\\-", "-").replace("\\.", ".")
            parts = title_text.split("-")
            brand = parts[0].strip()
            name = parts[1].strip() if len(parts) > 1 else ""
            
            skin_type = re.search(r"추천 피부 타입:\*\* (.*?)(?=\n|$)", body)
            concern = re.search(r"해결하려는 피부 고민:\*\* (.*?)(?=\n|$)", body)
            opinion = re.search(r"전문가 공통 의견:\*\* (.*?)(?=\n\*|$)", body, re.DOTALL)
            
            cur.execute("""
                INSERT INTO SE_products (brand, name, skin_type, concern, expert_opinion)
                VALUES (%s, %s, %s, %s, %s)
            """, (brand, name, 
                  skin_type.group(1).strip() if skin_type else "", 
                  concern.group(1).strip() if concern else "", 
                  opinion.group(1).strip() if opinion else ""))

    # --- 4. Expert Channels ---
    channel_file = "전문가 그룹별 뷰티 유튜브 채널 분석 리포트.md"
    channel_path = os.path.join(knowledge_path, channel_file)
    if os.path.exists(channel_path):
        with open(channel_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        cats = re.findall(r"### \d+.*?\.?\s*(.*?)\n(.*?)(?=###|$)", content, re.DOTALL)
        for cat_name, body in cats:
            channels = re.findall(r"\* \*\*(.*?):\*\* (.*?)(?=\n\*|$)", body)
            for ch_name, ch_desc in channels:
                cur.execute("""
                    INSERT INTO SE_expert_channels (name, category, description)
                    VALUES (%s, %s, %s)
                """, (ch_name.strip(), cat_name.strip(), ch_desc.strip()))

    # --- 5. Risks & Boosters ---
    guardian_file = "스킨케어 가디언_ 위험 요소 차단과 효과 극대화 전략.md"
    guardian_path = os.path.join(knowledge_path, guardian_file)
    if os.path.exists(guardian_path):
        with open(guardian_path, "r", encoding="utf-8") as f:
            content = f.read()
        cur.execute("INSERT INTO SE_knowledge_base (category, title, content) VALUES (%s, %s, %s)",
                    ("Safety", "Skincare Guardian: Risks & Boosters", content))

    conn.commit()
    cur.close()
    conn.close()
    print("[Migration] Final success attempt with ultra-flexible regex.")

if __name__ == "__main__":
    migrate_local_knowledge()
