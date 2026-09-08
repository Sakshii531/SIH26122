import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
print("Connecting to:", db_url)

conn = psycopg2.connect(db_url)
cur = conn.cursor()
cur.execute("""
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema='public' 
    ORDER BY table_name, ordinal_position;
""")
rows = cur.fetchall()

tables = {}
for table_name, column_name, data_type in rows:
    tables.setdefault(table_name, []).append((column_name, data_type))

for table, cols in tables.items():
    print(f"\nTable: {table}")
    for col, dt in cols:
        print(f"  - {col}: {dt}")
