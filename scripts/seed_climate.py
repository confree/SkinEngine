import psycopg2
import json

def seed_baseline_data():
    conn_params = {
        "host": "72.62.254.119",
        "user": "verisadmin",
        "password": "veris1234!",
        "dbname": "veriskin"
    }
    
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    
    # 1. SE_climate_logic (Hero/Villain mapping based on rules.md and science master)
    # Mapping generic climate zones to ingredients
    logic_data = [
        ("Tropical/Humid", ["Centella Asiatica", "Niacinamide", "BHA (Low dose)", "Lightweight Hyaluronic"], 
         ["Heavy Stearic Acid", "High-dose Retinol", "Mineral Oil"], 
         "현재 계정은 습도가 높은 기후에 있습니다. 모공 차단을 막는 세콜지 위주의 장벽 케어와 진정 위주의 루틴을 유지하세요."),
        
        ("Arid/Dry", ["Glycerin", "Ceramides", "Squalane", "Panthenol"], 
         ["High-content Alcohol", "Simple Hyaluronic (without occlusive)"], 
         "매우 건조한 환경입니다. 단순히 수분만 공급하기보다 유분막을 형성하는 세라마이드와 스쿠알란 성분을 필수로 사용하세요."),
        
        ("Cold/Arctic", ["Shea Butter", "Otot", "Ceramide EOP", "Vitamin E"], 
         ["Physical Exfoliators", "Acidic Toners"], 
         "한랭 건조한 기후는 피부 장벽을 쉽게 무너뜨립니다. 고보습 밤 형태의 제품으로 피부를 보호하세요."),
        
        ("Urban/Polluted", ["Antioxidants", "Vitamin C", "Ectoin", "Probiotics"], 
         ["Heavy Fragrances"], 
         "도시 공해로부터 피부를 보호하기 위해 항산화 성분과 마이크로바이옴 강화 성분을 추천합니다.")
    ]
    
    cur.execute("DELETE FROM SE_climate_logic")
    for zone, hero, villain, advice in logic_data:
        cur.execute("""
            INSERT INTO SE_climate_logic (climate_zone, hero_ingredients, villain_ingredients, advice_template)
            VALUES (%s, %s, %s, %s)
        """, (zone, hero, villain, advice))

    # 2. SE_climate_monthly (Initial Seed for 6 Key Cities)
    # Seeding Seoul (Temperate), Bangkok (Tropical), Dubai (Arid), London (Temperate), Paris (Temperate), NYC (Temperate)
    # This is a baseline, user can expand with Visual Crossing data.
    
    cities = [
        ("Seoul", "KR", [
            (1, -2, 40, 1), (4, 13, 50, 4), (7, 25, 80, 7), (10, 15, 55, 3)
        ]),
        ("Bangkok", "TH", [
            (1, 27, 60, 8), (4, 31, 65, 11), (7, 29, 75, 9), (10, 28, 80, 7)
        ]),
        ("Dubai", "AE", [
            (1, 19, 50, 6), (4, 27, 40, 10), (7, 36, 35, 12), (10, 30, 45, 9)
        ])
    ]
    
    # Simple interpolation to fill 12 months for these seed cities
    cur.execute("DELETE FROM SE_climate_monthly")
    for city, country, months in cities:
        # We only have 4 seasons above, let's just seed those for now as reference
        for m, t, h, uv in months:
            cur.execute("""
                INSERT INTO SE_climate_monthly (city, country_code, month, temp_avg, humidity_avg, uv_index_avg)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (city, month) DO UPDATE SET temp_avg=EXCLUDED.temp_avg, humidity_avg=EXCLUDED.humidity_avg
            """, (city, country, m, t, h, uv))

    conn.commit()
    cur.close()
    conn.close()
    print("[Seeding] Baseline climate logic and key cities seeded.")

if __name__ == "__main__":
    seed_baseline_data()
