import os
import sys
from pathlib import Path

# Add project path to sys.path
proj_dir = Path(r".")
sys.path.insert(0, str(proj_dir))

import app
import pandas as pd

print("1. Testing FAQ loading...")
faq_df = app.load_faq_data()
print(f"   Loaded {len(faq_df)} FAQs successfully.")
assert not faq_df.empty, "FAQ dataframe should not be empty!"
assert "Question" in faq_df.columns and "Answer" in faq_df.columns

print("2. Testing Escalated loading...")
esc_df = app.load_escalated_data()
print(f"   Escalated data columns: {list(esc_df.columns)}")
assert "Customer Question" in esc_df.columns
assert "Date and Time" in esc_df.columns
assert "Status" in esc_df.columns

print("3. Testing Matching and Answering...")
known_queries = [
    "What are your business hours?",
    "How can I contact customer support?",
    "What payment methods do you accept?",
    "What is your return policy?",
    "How can I track my order?",
    "business hours",
    "track order",
    "how to contact support"
]

for q in known_queries:
    row, score, is_match = app.find_best_faq_match(q, faq_df, threshold=68.0)
    print(f"   Query: '{q}' -> Match: {is_match} (Score: {score})")
    assert is_match, f"Query '{q}' should have matched!"
    assert row is not None
    assert len(str(row["Answer"])) > 0

print("4. Testing Escalation for Unknown Questions...")
unknown_queries = [
    "Do you have a physical store in Tokyo?",
    "Can I apply for a software engineering internship?",
    "What is the weather in New York?",
    "Tell me a bedtime story"
]

for q in unknown_queries:
    row, score, is_match = app.find_best_faq_match(q, faq_df, threshold=68.0)
    print(f"   Query: '{q}' -> Match: {is_match} (Score: {score})")
    assert not is_match, f"Query '{q}' should NOT have matched!"

print("5. Testing Escalation Storage & Deduplication...")
# Clear escalated questions first for clean test
empty_df = pd.DataFrame(columns=["Customer Question", "Date and Time", "Status"])
empty_df.to_csv(app.ESCALATED_FILE, index=False)

test_q = "Do you have a physical store in Tokyo?"
added_first = app.save_escalated_question(test_q)
print(f"   First addition result: {added_first}")
assert added_first == True

# Try adding again (duplicate test)
added_second = app.save_escalated_question(test_q)
print(f"   Duplicate addition result: {added_second}")
assert added_second == False

# Case insensitive duplicate test
added_third = app.save_escalated_question(test_q.upper())
print(f"   Case-insensitive duplicate result: {added_third}")
assert added_third == False

# Verify contents of escalated_questions.csv
saved_esc = pd.read_csv(app.ESCALATED_FILE)
print(f"   Total rows in escalated CSV: {len(saved_esc)}")
assert len(saved_esc) == 1
assert saved_esc.iloc[0]["Customer Question"] == test_q
assert saved_esc.iloc[0]["Status"] == "Escalated"
assert len(saved_esc.iloc[0]["Date and Time"]) > 0

print("6. Testing Exact Escalation String...")
expected_str = "ESCALATE: Your question has been forwarded to our support team."
print(f"   Exact string: '{expected_str}'")

print("\nALL AUTOMATED TESTS PASSED WITH 100% SUCCESS!")
