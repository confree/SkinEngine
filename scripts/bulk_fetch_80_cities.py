import requests
import psycopg2
import time
from typing import List

# API Key provided by user
VC_API_KEY = "978MRVGG2XR9MJP4Y9LGQUL2F"

# DB Connection params
DB_PARAMS = {
    "host": "72.62.254.119",
    "user": "verisadmin",
    "password": "veris1234!",
    "dbname": "veriskin"
}

# List of 80 Major Global Cities (Consolidated and verified)
CITIES = [
    # Asia
    "Seoul,KR", "Tokyo,JP", "Beijing,CN", "Shanghai,CN", "Hong Kong,HK", "Bangkok,TH", "Singapore,SG", "Jakarta,ID", 
    "Mumbai,IN", "New Delhi,IN", "Dubai,AE", "Riyadh,SA", "Ho Chi Minh City,VN", "Manila,PH", "Taipei,TW", 
    "Kuala Lumpur,MY", "Osaka,JP", "Nagoya,JP", "Hanoi,VN", "Da Nang,VN",
    # Europe
    "London,GB", "Paris,FR", "Berlin,DE", "Madrid,ES", "Rome,IT", "Amsterdam,NL", "Vienna,AT", "Prague,CZ", 
    "Warsaw,PL", "Stockholm,SE", "Oslo,NO", "Athens,GR", "Istanbul,TR", "Moscow,RU", "Zurich,CH", "Brussels,BE",
    # North America
    "New York City,NY", "Los Angeles,CA", "Chicago,IL", "Toronto,CA", "Vancouver,CA", "Mexico City,MX", "San Francisco,CA", 
    "Miami,FL", "Seattle,WA", "Houston,TX", "Atlanta,GA", "Boston,MA", "Dallas,TX", "Washington DC", "Montreal,CA",
    # Latin America
    "Sao Paulo,BR", "Buenos Aires,AR", "Bogota,CO", "Lima,PE", "Santiago,CL", "Rio de Janeiro,BR", "Panama City,PA", 
    "San Jose,CR", "Quito,EC", "Caracas,VE",
    # Oceania
    "Sydney,AU", "Melbourne,AU", "Auckland,NZ", "Brisbane,AU", "Perth,AU", "Gold Coast,AU", "Adelaide,AU", 
    "Canberra,AU", "Christchurch,NZ", "Hobart,AU",
    # Africa
    "Cairo,EG", "Johannesburg,ZA", "Nairobi,KE", "Lagos,NG", "Casablanca,MA", "Cape Town,ZA", "Marrakech,MA", 
    "Tunis,TN", "Algiers,DZ", "Addis Ababa,ET"
]

CITIES = list(dict.fromkeys(CITIES))[:80] # Preserve order and ensure uniqueness

def fetch_and_store_climate(city_query: str):
    print(f"[*] Processing {city_query}...")
    
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city_query}/2023-01-01/2023-12-31?unitGroup=metric&include=months,stats&key={VC_API_KEY}&contentType=json"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                city_name = city_query.split(",")[0].strip()
                country_code = city_query.split(",")[1] if "," in city_query else ""
                
                conn = psycopg2.connect(**DB_PARAMS)
                cur = conn.cursor()
                
                months = data.get("months", [])
                if not months:
                    print(f"    [!] No monthly data found for {city_name}")
                    return

                for m_data in months:
                    dt = m_data.get("datetime")
                    month_idx = int(dt.split("-")[1])
                    
                    cur.execute("""
                        INSERT INTO SE_climate_monthly (city, country_code, month, temp_avg, humidity_avg, uv_index_avg, precip_avg)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (city, month) DO UPDATE SET 
                            temp_avg = EXCLUDED.temp_avg,
                            humidity_avg = EXCLUDED.humidity_avg,
                            uv_index_avg = EXCLUDED.uv_index_avg,
                            precip_avg = EXCLUDED.precip_avg
                    """, (city_name, country_code, month_idx, m_data.get("temp"), m_data.get("humidity"), m_data.get("uvindex"), m_data.get("precip")))

                conn.commit()
                cur.close()
                conn.close()
                print(f"    [+] Success: {city_name}")
                return # Done with this city

            elif response.status_code == 429:
                print(f"    [!] Rate Limit (429). Retrying in {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(retry_delay)
                retry_delay *= 2 # Exponential backoff
            else:
                print(f"    [!] HTTP Error {response.status_code} for {city_query}")
                return

        except Exception as e:
            print(f"    [!] Exception for {city_query}: {e}")
            time.sleep(2)

def run_bulk_fetch():
    print(f"Starting Robust Bulk Fetch for {len(CITIES)} cities...")
    for city in CITIES:
        fetch_and_store_climate(city)
        time.sleep(3) # Safe delay between requests

if __name__ == "__main__":
    run_bulk_fetch()
