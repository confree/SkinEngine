import requests
import psycopg2
import time

# API Key provided by user
VC_API_KEY = "978MRVGG2XR9MJP4Y9LGQUL2F"

# DB Connection params
DB_PARAMS = {
    "host": "72.62.254.119",
    "user": "verisadmin",
    "password": "veris1234!",
    "dbname": "veriskin"
}

TOP_CITIES = [
    "Seoul,KR", "Bangkok,TH", "Dubai,AE", "London,GB", "Paris,FR", 
    "New York City,NY", "Tokyo,JP", "Singapore,SG", "Ho Chi Minh City,VN", "Sydney,AU"
]

def seed_top_cities():
    print(f"[*] Seeding Top {len(TOP_CITIES)} Global Cities...")
    for city in TOP_CITIES:
        try:
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/2023-01-01/2023-12-31?unitGroup=metric&include=months,stats&key={VC_API_KEY}&contentType=json"
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                months = data.get("months", [])
                city_name = city.split(",")[0].strip()
                
                conn = psycopg2.connect(**DB_PARAMS)
                cur = conn.cursor()
                
                for m_data in months:
                    dt = m_data.get("datetime")
                    month_idx = int(dt.split("-")[1])
                    
                    cur.execute("""
                        INSERT INTO SE_climate_monthly (city, country_code, month, temp_avg, humidity_avg, uv_index_avg, precip_avg)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (city, month) DO UPDATE SET 
                            temp_avg = EXCLUDED.temp_avg,
                            humidity_avg = EXCLUDED.humidity_avg,
                            uv_index_avg = EXCLUDED.uv_index_avg
                    """, (city_name, "", month_idx, m_data.get("temp"), m_data.get("humidity"), m_data.get("uvindex"), m_data.get("precip")))
                
                conn.commit()
                cur.close()
                conn.close()
                print(f"    [+] Seeded: {city_name}")
            else:
                print(f"    [!] Skip {city}: Status {response.status_code}")
            
            # Slow down to avoid 429
            time.sleep(5)
            
        except Exception as e:
            print(f"    [!] Error for {city}: {e}")

if __name__ == "__main__":
    seed_top_cities()
