import psycopg2
import requests
import datetime
from typing import Dict, Any, Optional

class ClimateManager:
    def __init__(self, db_params: Dict[str, str], vc_api_key: Optional[str] = None):
        self.db_params = db_params
        self.vc_api_key = vc_api_key

    def get_connection(self):
        return psycopg2.connect(**self.db_params)

    def get_refined_climate_context(self, city: str, current_temp: float, current_hum: float) -> str:
        """
        Combines current real-time weather with DB-stored monthly averages and expert logic.
        """
        month = datetime.datetime.now().month
        context = ""
        
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # 1. Fetch Monthly Averages for the city
            cur.execute("""
                SELECT temp_avg, humidity_avg, uv_index_avg 
                FROM SE_climate_monthly 
                WHERE city = %s AND month = %s
            """, (city, month))
            
            res = cur.fetchone()
            if not res and self.vc_api_key:
                # Dynamic Fetch from Visual Crossing if not in DB
                self._fetch_and_store_city_data(city)
                cur.execute("SELECT temp_avg, humidity_avg, uv_index_avg FROM SE_climate_monthly WHERE city = %s AND month = %s", (city, month))
                res = cur.fetchone()

            # 2. Determine Climate Zone and fetched Logic
            # Simplified mapping: Tropical if hum > 70 or (month avg hum > 70)
            hum_to_check = current_hum if current_hum else (res[1] if res else 50)
            temp_to_check = current_temp if current_temp else (res[0] if res else 20)
            
            zone = "Global Standard"
            if hum_to_check > 70:
                zone = "Tropical/Humid"
            elif hum_to_check < 35:
                zone = "Arid/Dry"
            elif temp_to_check < 5:
                zone = "Cold/Arctic"
                
            cur.execute("SELECT hero_ingredients, villain_ingredients, advice_template FROM SE_climate_logic WHERE climate_zone = %s", (zone,))
            logic = cur.fetchone()
            
            if not logic:
                cur.execute("SELECT hero_ingredients, villain_ingredients, advice_template FROM SE_climate_logic WHERE climate_zone = 'Global Standard'")
                logic = cur.fetchone()

            # 3. Construct Context String
            if res:
                context += f"지역 기후 통계({month}월): 평균 기온 {res[0]}C, 습도 {res[1]}%, UV지수 {res[2]}. "
            
            context += f"현재 기후 분류: {zone}. "
            context += f"권장 성분(Hero): {', '.join(logic[0])}. "
            context += f"기피 성분(Villain): {', '.join(logic[1])}. "
            context += f"전문가 조언: {logic[2]}"
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"[ClimateManager] Error: {e}")
            context = "기후 정보를 가져오는 중 오류가 발생했습니다. 표준 가이드를 적용합니다."
            
        return context

    def _fetch_and_store_city_data(self, city: str):
        """
        Fetch 12 months of averages from Visual Crossing and store in DB.
        """
        if not self.vc_api_key:
            return
            
        print(f"[ClimateManager] Dynamic fetch triggered for {city}...")
        try:
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}/2023-01-01/2023-12-31?unitGroup=metric&include=months,stats&key={self.vc_api_key}&contentType=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                months = data.get("months", [])
                
                conn = self.get_connection()
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
                    """, (city, "", month_idx, m_data.get("temp"), m_data.get("humidity"), m_data.get("uvindex"), m_data.get("precip")))
                
                conn.commit()
                cur.close()
                conn.close()
                print(f"[ClimateManager] Successfully indexed {city}.")
            else:
                print(f"[ClimateManager] API Skip ({city}): Status {response.status_code}")
                
        except Exception as e:
            print(f"[ClimateManager] Dynamic fetch failed: {e}")
