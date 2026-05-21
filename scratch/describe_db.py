import psycopg2
PG_CONFIG = {
    'host': '72.62.254.119',
    'database': 'veriskin',
    'user': 'verisadmin',
    'password': 'veris1234!'
}
def describe_table():
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'unified_global_products'")
        columns = cur.fetchall()
        for col in columns:
            print(f"{col[0]}: {col[1]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    describe_table()
