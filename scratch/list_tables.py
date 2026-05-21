import psycopg2
PG_CONFIG = {
    'host': '72.62.254.119',
    'database': 'veriskin',
    'user': 'verisadmin',
    'password': 'veris1234!'
}
def list_tables():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cur.fetchall()
        for table in tables:
            print(table[0])
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    list_tables()
