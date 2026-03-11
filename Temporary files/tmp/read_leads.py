import sqlite3
import json

def check_leads():
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leads")
        rows = cursor.fetchall()
        print(f"Total leads: {len(rows)}")
        for row in rows:
            print(row)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_leads()
