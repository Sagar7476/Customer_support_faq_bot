from rapidfuzz import fuzz, process
import pandas as pd

df = pd.read_csv(r"FAQ.csv")
questions = df["Question"].tolist()

def get_best_match(query, questions):
    best_q = None
    best_score = 0.0
    best_idx = -1
    for i, q in enumerate(questions):
        # We can evaluate token_set_ratio and token_sort_ratio
        score_sort = fuzz.token_sort_ratio(query, q)
        score_set = fuzz.token_set_ratio(query, q)
        # partial ratio can be useful if query is a direct substring of question (e.g. "business hours")
        score_partial = fuzz.partial_ratio(query.lower(), q.lower()) if len(query.strip()) >= 5 else 0
        
        # If the user query is very short compared to the question, partial_ratio might give false positives
        # so we weight it or take a blended approach:
        # e.g., if token_set_ratio is decent or partial_ratio with token overlap
        combined = max(score_sort, score_set)
        if score_partial >= 85 and len(query.split()) >= 2:
            combined = max(combined, score_partial * 0.85) # give partial a bounded boost

        if combined > best_score:
            best_score = combined
            best_q = q
            best_idx = i
    return best_q, best_score, best_idx

test_queries = [
    "What are your business hours?",
    "business hours please",
    "business hours",
    "when are you open?",
    "how can I contact customer support?",
    "customer support phone number",
    "payment methods",
    "what payment methods do you accept?",
    "what is your return policy?",
    "return policy",
    "how to track my order",
    "track order",
    "Do you have a physical store in Tokyo?",
    "Can I apply for a job as a software engineer at your company?",
    "What is the weather today?",
    "How do I cancel my order?",
    "cancel order",
    "Where is my receipt?",
    "who is the president of france?",
    "tell me a joke"
]

print("=== Testing Matching Function ===")
for q in test_queries:
    match_q, score, idx = get_best_match(q, questions)
    status = "MATCH" if score >= 65 else "ESCALATE"
    print(f"[{status}] (Score: {score:4.1f}) Query: '{q}' -> '{match_q}'")
