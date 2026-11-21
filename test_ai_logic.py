import re
import pandas as pd

def classify_and_generate_offline(query: str, faq_df: pd.DataFrame) -> tuple[str, str]:
    """
    Intelligent offline fallback when no API key is configured.
    Distinguishes general questions from inquiries requiring company-specific information.
    """
    q_lower = query.strip().lower()

    # 1. Company-specific keywords requiring official human support
    escalation_triggers = [
        "tokyo", "physical store", "retail store", "branch", "headquarters", "address",
        "job", "hiring", "career", "internship", "vacancy", "resume",
        "order #", "order number", "my order id", "track #",
        "custom discount", "wholesale price", "quote", "bulk contract",
        "complaint", "legal", "lawsuit", "manager", "ceo", "director", "owner"
    ]
    if any(trigger in q_lower for trigger in escalation_triggers):
        return ("This inquiry requires official company-specific information not available in our public FAQ.", "ESCALATE")

    # 2. General conversational greetings
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings"]
    if any(q_lower == g or q_lower.startswith(g + " ") for g in greetings):
        return ("Hello! 👋 I am your automated AI support assistant. I can help answer common questions about our store policies, business hours, payments, and general shopping advice. How may I assist you today?", "AI")

    # 3. Gratitude / Closing
    thanks = ["thank you", "thanks", "appreciate it", "bye", "goodbye"]
    if any(t in q_lower for t in thanks):
        return ("You're very welcome! If you have any other questions, feel free to ask anytime. Have a wonderful day! 😊", "AI")

    # 4. General ecommerce definitions / advice
    if "business day" in q_lower:
        return ("A 'business day' typically refers to standard working days (Monday through Friday), excluding weekends and official public holidays. Shipping estimates are usually calculated in business days.", "AI")
    
    if "invoice" in q_lower and "what is" in q_lower:
        return ("An invoice is an itemized commercial document that records the products or services delivered to a customer, total amount due, taxes, and payment terms.", "AI")

    if "sizing" in q_lower or "size" in q_lower:
        return ("For best sizing results when shopping online, we recommend measuring your bust/chest, waist, and hips with a soft measuring tape and comparing them to the sizing guide provided on the product page.", "AI")

    # Default fallback for unhandled unknown queries without an API key -> escalate to be safe
    return ("This question may require specific company verification.", "ESCALATE")

# Test queries
faq_df = pd.DataFrame()
test_cases = [
    ("Hello there!", "AI"),
    ("What are business days?", "AI"),
    ("Do you have a physical store in Tokyo?", "ESCALATE"),
    ("Can I apply for a job or internship?", "ESCALATE"),
    ("Thank you for your help!", "AI"),
]

print("=== Testing Offline AI Fallback ===")
for q, expected in test_cases:
    ans, t = classify_and_generate_offline(q, faq_df)
    status = "PASS" if t == expected else "FAIL"
    print(f"[{status}] Query: '{q}' -> Type: {t} | Ans: {ans[:60]}...")
