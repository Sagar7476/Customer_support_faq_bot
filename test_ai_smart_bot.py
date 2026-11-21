import sys
from pathlib import Path
import sqlite3
import pandas as pd

proj_dir = Path(r".")
sys.path.insert(0, str(proj_dir))

import app

print("=== 1. VERIFY FAQ CSV FIRST SEARCH ===")
faq_df = app.load_faq_data()
assert not faq_df.empty

known_q = "What are your business hours?"
match_row, score, is_match = app.find_best_faq_match(known_q, faq_df)
print(f"Known Query: '{known_q}' -> is_match: {is_match}, score: {score}")
assert is_match == True
assert "Monday through Friday" in str(match_row["Answer"])

known_q2 = "What payment methods do you accept?"
match_row2, score2, is_match2 = app.find_best_faq_match(known_q2, faq_df)
print(f"Known Query 2: '{known_q2}' -> is_match: {is_match2}, score: {score2}")
assert is_match2 == True
assert "PayPal" in str(match_row2["Answer"])

print("\n=== 2. VERIFY SMART AI GENERAL QUESTIONS (NO ESCALATION) ===")
general_queries = [
    "Hello there!",
    "Can you explain how online shopping works?",
    "What is an invoice and why is it needed?",
    "Thank you for your help!"
]

for gq in general_queries:
    row, s, matched = app.find_best_faq_match(gq, faq_df)
    ans, r_type = app.generate_ai_response(gq, faq_df, api_key=None)
    print(f"General Query: '{gq}' -> FAQ Match: {matched} | AI Response Type: {r_type} | Ans: {ans[:55]}...")
    assert not matched, f"General query '{gq}' should not match FAQ"
    assert r_type == "AI", f"General query '{gq}' should be answered by AI, not escalated!"
    assert len(ans) > 10

print("\n=== 3. VERIFY GENUINE ESCALATION CASES (COMPANY-SPECIFIC UNKNOWN) ===")
escalate_queries = [
    "Do you have a physical retail store in Tokyo?",
    "Can I apply for a job or internship at your company?",
    "What is the personal phone number of the company CEO?",
    "Can you give me a custom bulk quote for 1000 units?"
]

for eq in escalate_queries:
    row, s, matched = app.find_best_faq_match(eq, faq_df)
    ans, r_type = app.generate_ai_response(eq, faq_df, api_key=None)
    print(f"Company Query: '{eq}' -> FAQ Match: {matched} | AI Response Type: {r_type} | Reason: {ans[:55]}...")
    assert not matched, f"Escalate query '{eq}' should not match FAQ"
    assert r_type == "ESCALATE", f"Company query '{eq}' MUST be escalated!"

print("\n=== 4. VERIFY TICKET LOGGING & ADMIN REPLY WORKFLOW ===")
t_id, is_new = app.create_or_get_ticket("Do you have a physical store in Tokyo?")
print(f"Created ticket: {t_id}")
assert t_id.startswith("TCK-")

t_data = app.get_ticket_by_id(t_id)
assert t_data is not None

reply_msg = "Hello! We currently operate exclusively online and do not have a physical store in Tokyo."
app.submit_admin_reply(t_id, reply_msg)

t_resolved = app.get_ticket_by_id(t_id)
assert t_resolved["status"] == "Resolved"
assert t_resolved["admin_reply"] == reply_msg
print(f"Ticket Status after reply: {t_resolved['status']}")

print("\n=== 5. VERIFY API KEY RETRIEVAL LOGIC ===")
active_key = app.get_active_api_key()
print(f"Active Key detected: {bool(active_key)}")

print("\nALL AI-POWERED CHATBOT TESTS PASSED WITH 100% SUCCESS!")
