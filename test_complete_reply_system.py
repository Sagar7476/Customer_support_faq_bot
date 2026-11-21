import sys
from pathlib import Path
import sqlite3
import pandas as pd

proj_dir = Path(r".")
sys.path.insert(0, str(proj_dir))

import app

print("=== STEP 1: INITIALIZE DB & VERIFY SCHEMA ===")
app.init_sqlite_db()
assert app.DB_FILE.exists(), "Database file must exist!"

# Reset DB for test isolation
with sqlite3.connect(app.DB_FILE) as conn:
    conn.execute("DELETE FROM tickets")
    conn.commit()

print("=== STEP 2: TEST TICKET CREATION & ID GENERATION ===")
q1 = "Do you have a physical store in Tokyo?"
t_id1, is_new1 = app.create_or_get_ticket(q1)
print(f"Created ticket 1: {t_id1}, is_new: {is_new1}")
assert t_id1 == "TCK-1001"
assert is_new1 == True

# Duplicate pending question check
t_id1_dup, is_new1_dup = app.create_or_get_ticket(q1)
print(f"Duplicate question check: {t_id1_dup}, is_new: {is_new1_dup}")
assert t_id1_dup == "TCK-1001"
assert is_new1_dup == False

q2 = "Can I apply for a software engineering internship?"
t_id2, is_new2 = app.create_or_get_ticket(q2)
print(f"Created ticket 2: {t_id2}, is_new: {is_new2}")
assert t_id2 == "TCK-1002"
assert is_new2 == True

print("=== STEP 3: CHECK INITIAL TICKET COUNTS ===")
counts1 = app.get_ticket_counts()
print(f"Initial Counts: Total={counts1['total']}, Pending={counts1['pending']}, Resolved={counts1['resolved']}")
assert counts1["total"] == 2
assert counts1["pending"] == 2
assert counts1["resolved"] == 0

print("=== STEP 4: SUBMIT ADMIN REPLY ===")
reply_text = "Hi! We do not currently operate a physical store in Tokyo, but we ship internationally to Japan in 7-10 business days."
success = app.submit_admin_reply(t_id1, reply_text)
assert success == True
print(f"Submitted reply to {t_id1}: success={success}")

print("=== STEP 5: VERIFY TICKET STATUS CHANGED TO RESOLVED ===")
ticket1_data = app.get_ticket_by_id(t_id1)
print("Ticket 1 Data after reply:", ticket1_data)
assert ticket1_data["status"] == "Resolved"
assert ticket1_data["admin_reply"] == reply_text
assert ticket1_data["reply_time"] is not None

print("=== STEP 6: CHECK UPDATED COUNTS ===")
counts2 = app.get_ticket_counts()
print(f"Updated Counts: Total={counts2['total']}, Pending={counts2['pending']}, Resolved={counts2['resolved']}")
assert counts2["total"] == 2
assert counts2["pending"] == 1
assert counts2["resolved"] == 1

print("=== STEP 7: TEST CUSTOMER TRACKING LOOKUP ===")
# Exact match
cust_view1 = app.get_ticket_by_id("TCK-1001")
assert cust_view1 is not None and cust_view1["admin_reply"] == reply_text
# Case-insensitive match (lowercase)
cust_view_lower = app.get_ticket_by_id("tck-1001")
assert cust_view_lower is not None and cust_view_lower["status"] == "Resolved"
# Pending ticket lookup
cust_view2 = app.get_ticket_by_id("TCK-1002")
assert cust_view2 is not None and cust_view2["status"] == "Pending" and cust_view2["admin_reply"] is None
# Invalid ticket lookup
cust_view_invalid = app.get_ticket_by_id("TCK-9999")
assert cust_view_invalid is None
print("Customer tracking tests passed!")

print("=== STEP 8: VERIFY CSV SYNCHRONIZATION ===")
assert app.ESCALATED_FILE.exists()
csv_df = pd.read_csv(app.ESCALATED_FILE)
print("Escalated CSV Columns:", list(csv_df.columns))
print(f"Escalated CSV Row count: {len(csv_df)}")
assert len(csv_df) == 2
assert "Ticket ID" in csv_df.columns
assert "Status" in csv_df.columns
assert "Admin Reply" in csv_df.columns

print("\nALL SQLITE & ADMIN REPLY TESTS PASSED WITH 100% SUCCESS!")
