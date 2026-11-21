from rapidfuzz import fuzz
import pandas as pd
import re

df = pd.read_csv(r"FAQ.csv")
questions = df["Question"].tolist()

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()

def match_query(query, faq_list):
    q_clean = clean_text(query)
    best_match = None
    best_score = 0.0
    best_idx = -1
    
    for i, orig_q in enumerate(faq_list):
        faq_clean = clean_text(orig_q)
        r = fuzz.ratio(q_clean, faq_clean)
        tsort = fuzz.token_sort_ratio(q_clean, faq_clean)
        tset = fuzz.token_set_ratio(q_clean, faq_clean)
        pr = fuzz.partial_ratio(q_clean, faq_clean)
        
        # When query is short, partial_ratio can be high by chance on long sentences.
        # So we only consider partial_ratio if query has enough length or words
        if len(q_clean.split()) >= 2 and len(q_clean) >= 8:
            candidate_score = max(r, tsort, tset, pr)
        else:
            candidate_score = max(r, tsort, tset)
            
        if candidate_score > best_score:
            best_score = candidate_score
            best_match = orig_q
            best_idx = i
            
    return best_match, best_score, best_idx

test_queries = [
    ("What are your business hours?", True),
    ("business hours please", True),
    ("business hours", True),
    ("what time do you close?", False), # or escalate if not in FAQ
    ("how can I contact customer support?", True),
    ("contact customer support", True),
    ("what payment methods do you accept?", True),
    ("payment methods", True),
    ("can I pay with credit card?", False), # or escalate
    ("what is your return policy?", True),
    ("return policy", True),
    ("how can I track my order?", True),
    ("track order", True),
    ("Do you have a physical store in Tokyo?", False),
    ("Can I apply for a job as a software engineer?", False),
    ("What is the weather today?", False),
    ("How do I cancel my order?", True),
    ("Where is my invoice?", True),
    ("who is the president of france?", False),
    ("tell me a joke", False)
]

print("=== Evaluation (Threshold = 65) ===")
for q, expected_match in test_queries:
    best_q, score, idx = match_query(q, questions)
    matched = score >= 65
    verdict = "OK" if matched == expected_match else "MISMATCH"
    action = "ANSWER" if matched else "ESCALATE"
    print(f"[{verdict}] [{action}] (Score: {score:4.1f}) Query: '{q}' -> '{best_q}'")
