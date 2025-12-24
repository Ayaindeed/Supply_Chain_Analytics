import psycopg2
try:
    conn = psycopg2.connect('postgresql://postgres:postgres@postgres:5432/supply_chain_dw')
    cur = conn.cursor()
    cur.execute('SELECT current_database()')
    print('✅ Connected to:', cur.fetchone()[0])
    conn.close()
    print('✅ Connection test successful!')
except Exception as e:
    print('❌ Connection failed:', str(e))
