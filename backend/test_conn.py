import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv('DATABASE_URL')
print(f"Connecting to: {db_url}")

try:
    conn = psycopg2.connect(db_url)
    print("Successfully connected!")
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print(f"Result: {cur.fetchone()}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
