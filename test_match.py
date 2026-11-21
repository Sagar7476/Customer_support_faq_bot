from rapidfuzz import fuzz, process
import pandas as pd

df = pd.read_csv(r"FAQ.csv")
questions = df["Question"].tolist()

test_queries = [
    "What are your business hours?",
    "business hours please",
    "when are you open?",
    "how can I pay for my order?",
    "can I pay using Paypal?",
    "what is your return policy?",
    "how to track my package",
    "Do you have a physical store in Tokyo?",
    "Can I apply for a job as a software engineer at your company?",
    "What is the weather today?",
    "How do I cancel my order?",
    "Where is my receipt?",
]

print("=== Testing token_sort_ratio ===")
for q in test_queries:
    match, score, idx = process.extractOne(q, questions, scorer=fuzz.token_sort_ratio)
    print(f"Query: '{q}' -> Match: '{match}' | Score: {score:.1f}")

print("\n=== Testing token_set_ratio ===")
for q in test_queries:
    match, score, idx = process.extractOne(q, questions, scorer=fuzz.token_set_ratio)
    print(f"Query: '{q}' -> Match: '{match}' | Score: {score:.1f}")
