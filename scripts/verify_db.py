import psycopg2

def verify_tables():
    conn_params = {
        "host": "72.62.254.119",
        "user": "verisadmin",
        "password": "veris1234!",
        "dbname": "veriskin"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'se_%';
        """)
        
        tables = cur.fetchall()
        print(f"Detected Tables ({len(tables)}):")
        for table in tables:
            print(f"- {table[0]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    verify_tables()
