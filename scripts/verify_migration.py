import psycopg2

def verify_data():
    conn_params = {
        "host": "72.62.254.119",
        "user": "verisadmin",
        "password": "veris1234!",
        "dbname": "veriskin"
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        tables = [
            "SE_knowledge_base", "SE_safety_guards", "SE_products", 
            "SE_routines", "SE_expert_channels"
        ]
        
        print("Table Record Counts:")
        for table in tables:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"- {table}: {count}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    verify_data()
