import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

DB_FILE = Path(r"C:\Users\sagar\.gemini\antigravity\brain\cc86e20e-461a-4e72-9b87-a5d125f6af38\scratch\test_tickets.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            customer_question TEXT NOT NULL,
            date_time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            admin_reply TEXT,
            reply_time TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_ticket_id():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT ticket_id FROM tickets WHERE ticket_id LIKE 'TCK-%' ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        try:
            num = int(row[0].split("-")[1])
            return f"TCK-{num + 1}"
        except (IndexError, ValueError):
            pass
    return "TCK-1001"

def create_ticket(question: str):
    clean_q = question.strip()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check for existing pending duplicate
    cursor.execute("SELECT ticket_id FROM tickets WHERE LOWER(TRIM(customer_question)) = LOWER(?) AND status = 'Pending'", (clean_q,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0], False

    ticket_id = generate_ticket_id()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO tickets (ticket_id, customer_question, date_time, status, admin_reply, reply_time) VALUES (?, ?, ?, 'Pending', NULL, NULL)",
        (ticket_id, clean_q, now_str)
    )
    conn.commit()
    conn.close()
    return ticket_id, True

def get_ticket(ticket_id: str):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE UPPER(TRIM(ticket_id)) = UPPER(TRIM(?))", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def reply_to_ticket(ticket_id: str, reply: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "UPDATE tickets SET admin_reply = ?, reply_time = ?, status = 'Resolved' WHERE UPPER(TRIM(ticket_id)) = UPPER(TRIM(?))",
        (reply.strip(), now_str, ticket_id)
    )
    conn.commit()
    conn.close()
    return True

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END), SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) FROM tickets")
    row = cursor.fetchone()
    conn.close()
    total = row[0] or 0
    pending = row[1] or 0
    resolved = row[2] or 0
    return {"total": total, "pending": pending, "resolved": resolved}

init_db()
print("1. Creating ticket 1...")
t1, is_new1 = create_ticket("Do you have a store in Tokyo?")
print(f"Created: {t1}, New: {is_new1}")
assert t1 == "TCK-1001" and is_new1 == True

print("2. Duplicate ticket check...")
t2, is_new2 = create_ticket("Do you have a store in Tokyo?")
print(f"Duplicate check: {t2}, New: {is_new2}")
assert t2 == "TCK-1001" and is_new2 == False

print("3. Creating ticket 2...")
t3, is_new3 = create_ticket("Can I apply for a job?")
print(f"Created: {t3}, New: {is_new3}")
assert t3 == "TCK-1002" and is_new3 == True

print("4. Testing Stats...")
stats = get_stats()
print("Stats:", stats)
assert stats["total"] == 2 and stats["pending"] == 2 and stats["resolved"] == 0

print("5. Replying to TCK-1001...")
reply_to_ticket("TCK-1001", "Hello! We currently do not have a physical store in Tokyo, but we ship directly from our regional warehouse.")
ticket_details = get_ticket("TCK-1001")
print("Ticket details after reply:", ticket_details)
assert ticket_details["status"] == "Resolved"
assert "Tokyo" in ticket_details["admin_reply"]

print("6. Testing Stats after reply...")
stats = get_stats()
print("Updated Stats:", stats)
assert stats["total"] == 2 and stats["pending"] == 1 and stats["resolved"] == 1

print("\nALL SQLITE TICKET TESTS PASSED SUCCESSFULLY!")
