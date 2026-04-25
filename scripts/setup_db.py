import psycopg2
from psycopg2 import sql

def setup_database():
    conn_params = {
        "host": "72.62.254.119",
        "user": "verisadmin",
        "password": "veris1234!",
        "dbname": "veriskin"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        # 1. SE_knowledge_base (General Rules, Persona, etc.)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SE_knowledge_base (
                id SERIAL PRIMARY KEY,
                category VARCHAR(50) NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. SE_safety_guards (Prohibitions & Warnings)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SE_safety_guards (
                id SERIAL PRIMARY KEY,
                target_group VARCHAR(100), -- BIPOC, Tropical, etc.
                prohibited_items TEXT[],
                risk_description TEXT,
                severity VARCHAR(20) DEFAULT 'critical',
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. SE_products (Expert Recommended Products)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SE_products (
                id SERIAL PRIMARY KEY,
                brand VARCHAR(100),
                name VARCHAR(200),
                skin_type VARCHAR(50),
                concern VARCHAR(100),
                expert_opinion TEXT,
                viral_status VARCHAR(100),
                ingredients TEXT[],
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 4. SE_routines (Standard Protocols)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SE_routines (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE,
                description TEXT,
                steps JSONB, -- List of steps with products
                target_user VARCHAR(100),
                climate_suitability VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 5. SE_climate_monthly (Historical Climate Data)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SE_climate_monthly (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                country_code VARCHAR(10),
                month SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
                temp_avg FLOAT,
                humidity_avg FLOAT,
                uv_index_avg FLOAT,
                precip_avg FLOAT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, month)
            );
        """)

        # 6. SE_climate_logic (Ingredient Hero/Villain per climate)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SE_climate_logic (
                id SERIAL PRIMARY KEY,
                climate_zone VARCHAR(50), -- Tropical, Arid, Cold, etc.
                hero_ingredients TEXT[],
                villain_ingredients TEXT[],
                advice_template TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 7. SE_expert_channels (Source Intelligence)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS SE_expert_channels (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50), -- Doctor, Artist, Influencer
                specialization TEXT,
                trust_level SMALLINT DEFAULT 5, -- 1 to 10
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("✅ [Database-Setup] All SE_ tables created successfully.")
        
    except Exception as e:
        print(f"❌ [Database-Setup] Error: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    setup_database()
