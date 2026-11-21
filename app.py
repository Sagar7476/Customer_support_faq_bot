"""
AI-Powered Customer Support FAQ Bot & Support Ticket System
A comprehensive mini-project built with Streamlit, Pandas, RapidFuzz, SQLite, and Google GenAI.

Key Highlights:
1. FAQ-First Search: RapidFuzz searches the verified FAQ CSV knowledge base first.
2. Smart AI Fallback: Generates helpful AI answers for general customer inquiries.
3. Strict Company Escalation: Automatically escalates unknown company-specific queries to human support.
4. SQLite Ticket System: Generates unique Ticket IDs, stores tickets, replies, and status permanently.
5. Customer Ticket Tracking: Allows customers to enter their Ticket ID to read official support replies.
6. Admin Reply Console: Allows support teams to inspect pending tickets, write replies, and mark as resolved.
7. Clear Badge Distinction: Differentiates FAQ answers, AI answers, and escalated inquiries.
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
from rapidfuzz import fuzz

# ==========================================
# PAGE CONFIGURATION & THEME STYLING
# ==========================================
st.set_page_config(
    page_title="Smart Customer Support FAQ Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Blue and White Theme CSS with AI badges
CUSTOM_CSS = """
<style>
    /* Global styles */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        color: white;
        padding: 24px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.15);
    }
    .main-header h1 {
        color: white !important;
        font-size: 26px;
        font-weight: 700;
        margin: 0;
        padding: 0;
    }
    .main-header p {
        color: #E0E7FF;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Metric cards */
    .metric-container {
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        flex: 1;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #2563EB;
    }
    .metric-card.pending {
        border-left: 5px solid #F59E0B;
    }
    .metric-card.resolved {
        border-left: 5px solid #10B981;
    }
    .metric-card.total {
        border-left: 5px solid #3B82F6;
    }
    .metric-title {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
    }

    /* Chat bubble enhancements */
    .chat-timestamp {
        font-size: 11px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* Verified FAQ badge */
    .matched-badge {
        display: inline-block;
        background-color: #DBEAFE;
        color: #1E40AF;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-bottom: 6px;
        border: 1px solid #93C5FD;
    }
    
    /* Smart AI Response badge */
    .ai-badge {
        display: inline-block;
        background-color: #F3E8FF;
        color: #6B21A8;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-bottom: 6px;
        border: 1px solid #D8B4FE;
    }
    
    /* Escalated Ticket badge */
    .escalate-badge {
        display: inline-block;
        background-color: #FEE2E2;
        color: #991B1B;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-bottom: 6px;
        border: 1px solid #FCA5A5;
    }
    .ticket-badge {
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-left: 6px;
        border: 1px solid #FCD34D;
    }

    /* Ticket card styling */
    .ticket-display-box {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 16px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
    .reply-box {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 5px solid #16A34A;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 14px;
    }
    .pending-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 5px solid #D97706;
        border-radius: 10px;
        padding: 16px 20px;
        margin-top: 14px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==========================================
# FILE PATHS & DATABASE SETUP
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
FAQ_FILE = BASE_DIR / "FAQ.csv"
ESCALATED_FILE = BASE_DIR / "escalated_questions.csv"
DB_FILE = BASE_DIR / "support_tickets.db"

DEFAULT_FAQS = [
    ("What are your business hours?", "Our customer support team is available Monday through Friday from 9:00 AM to 6:00 PM EST. On weekends, our support is limited to emergency escalations."),
    ("How can I contact customer support?", "You can reach our customer support team via email at support@example.com or call our toll-free number at 1-800-555-0199 during business hours."),
    ("What payment methods do you accept?", "We accept all major credit and debit cards (Visa, MasterCard, American Express, Discover), PayPal, Apple Pay, and Google Pay."),
    ("What is your return policy?", "We offer a 30-day hassle-free return policy. Items must be in their original condition and packaging. Return shipping is free for damaged or defective items."),
    ("How can I track my order?", "Once your order is shipped, you will receive an email with a tracking number and a direct link to track your shipment in real time."),
    ("How long does shipping take?", "Standard domestic shipping takes 3 to 5 business days. Express shipping takes 1 to 2 business days. International shipping typically takes 7 to 14 business days."),
    ("Can I change or cancel my order?", "You can modify or cancel your order within 1 hour of placing it by visiting your Account Orders page or contacting our support desk immediately."),
    ("Do you ship internationally?", "Yes, we ship to over 50 countries worldwide. International shipping rates and duties are calculated at checkout based on destination."),
    ("How do I reset my account password?", "Click on the 'Forgot Password' link on the login page, enter your registered email address, and follow the password reset link sent to your inbox."),
    ("Where can I find my invoice?", "Invoices are sent to your registered email address right after purchase and can also be downloaded anytime from your Account Dashboard under 'Billing'."),
    ("What should I do if I received a damaged item?", "Please report damaged items within 48 hours of delivery by sending photos of the damage to support@example.com, and we will dispatch a free replacement immediately."),
    ("Do you offer discounts for students or bulk purchases?", "Yes! We offer a 15% discount for verified students and special tier pricing for bulk commercial orders. Contact sales@example.com for details."),
    ("Is my payment and personal information secure?", "Yes, all transactions are encrypted using 256-bit SSL encryption, and we are fully PCI-DSS compliant. We never store complete card details on our servers."),
    ("How do I create a new customer account?", "Click the 'Sign Up' button at the top right of our website, enter your name, email, and choose a secure password to activate your account in seconds."),
    ("Can I exchange an item instead of returning it?", "Yes, exchanges can be requested within 30 days of purchase through our Online Return Portal by choosing 'Exchange for a different size/color'."),
]


def init_sqlite_db():
    """Initialize SQLite database table for tickets."""
    with sqlite3.connect(DB_FILE) as conn:
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


# Initialize database
init_sqlite_db()


def load_faq_data() -> pd.DataFrame:
    """Load FAQ.csv or generate default file if missing or corrupted."""
    if not FAQ_FILE.exists() or os.path.getsize(FAQ_FILE) == 0:
        df = pd.DataFrame(DEFAULT_FAQS, columns=["Question", "Answer"])
        df.to_csv(FAQ_FILE, index=False)
        return df

    try:
        df = pd.read_csv(FAQ_FILE)
        col_map = {c: c.strip().capitalize() for c in df.columns}
        df = df.rename(columns=col_map)
        
        if "Question" not in df.columns or "Answer" not in df.columns:
            st.warning("FAQ.csv had missing columns. Re-creating with valid schema.")
            df = pd.DataFrame(DEFAULT_FAQS, columns=["Question", "Answer"])
            df.to_csv(FAQ_FILE, index=False)
        return df
    except Exception as e:
        st.error(f"Error loading FAQ.csv: {e}. Restoring default FAQ dataset.")
        df = pd.DataFrame(DEFAULT_FAQS, columns=["Question", "Answer"])
        df.to_csv(FAQ_FILE, index=False)
        return df


def generate_ticket_id() -> str:
    """Generate the next unique Ticket ID (e.g., TCK-1001, TCK-1002)."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_id FROM tickets WHERE ticket_id LIKE 'TCK-%' ORDER BY rowid DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row[0]:
            try:
                num = int(row[0].split("-")[1])
                return f"TCK-{num + 1}"
            except (IndexError, ValueError):
                pass
    return "TCK-1001"


def sync_db_to_csv():
    """Synchronize SQLite tickets into escalated_questions.csv."""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(
            "SELECT ticket_id AS 'Ticket ID', customer_question AS 'Customer Question', date_time AS 'Date and Time', status AS 'Status', admin_reply AS 'Admin Reply', reply_time AS 'Reply Time' FROM tickets ORDER BY rowid DESC",
            conn
        )
    df.to_csv(ESCALATED_FILE, index=False)


def create_or_get_ticket(question: str) -> tuple[str, bool]:
    """
    Save an unknown question to SQLite.
    Avoids duplicate entries if the question is already 'Pending'.
    Returns (ticket_id, is_new).
    """
    cleaned_q = question.strip()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ticket_id FROM tickets WHERE LOWER(TRIM(customer_question)) = LOWER(?) AND status = 'Pending'",
            (cleaned_q,)
        )
        existing = cursor.fetchone()
        if existing:
            return existing[0], False

        ticket_id = generate_ticket_id()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO tickets (ticket_id, customer_question, date_time, status, admin_reply, reply_time) VALUES (?, ?, ?, 'Pending', NULL, NULL)",
            (ticket_id, cleaned_q, now_str)
        )
        conn.commit()

    sync_db_to_csv()
    return ticket_id, True


def get_all_tickets() -> pd.DataFrame:
    """Fetch all tickets from SQLite as a DataFrame."""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(
            "SELECT ticket_id, customer_question, date_time, status, admin_reply, reply_time FROM tickets ORDER BY rowid DESC",
            conn
        )
    return df


def get_ticket_by_id(ticket_id: str) -> dict | None:
    """Fetch a single ticket by its Ticket ID (case-insensitive)."""
    clean_id = ticket_id.strip()
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tickets WHERE UPPER(TRIM(ticket_id)) = UPPER(TRIM(?))",
            (clean_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def submit_admin_reply(ticket_id: str, reply_text: str) -> bool:
    """Save admin reply to SQLite, change status to Resolved, and sync CSV."""
    clean_reply = reply_text.strip()
    if not clean_reply:
        return False

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tickets SET admin_reply = ?, reply_time = ?, status = 'Resolved' WHERE UPPER(TRIM(ticket_id)) = UPPER(TRIM(?))",
            (clean_reply, now_str, ticket_id)
        )
        conn.commit()

    sync_db_to_csv()
    return True


def get_ticket_counts() -> dict:
    """Return dictionary of total, pending, and resolved counts."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*),
                SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END)
            FROM tickets
        """)
        row = cursor.fetchone()
        total = row[0] or 0
        pending = row[1] or 0
        resolved = row[2] or 0
        return {"total": total, "pending": pending, "resolved": resolved}


# ==========================================
# FUZZY MATCHING ALGORITHM (FIRST SEARCH)
# ==========================================
def find_best_faq_match(user_query: str, faq_df: pd.DataFrame, threshold: float = 68.0):
    """
    Step 1: Searches the existing FAQ CSV for every customer question.
    Combines token sort, token set, and full ratio for optimal accuracy.
    Returns (matched_row, similarity_score, is_match).
    """
    if faq_df.empty or not user_query.strip():
        return None, 0.0, False

    clean_query = user_query.strip().lower()
    best_score = 0.0
    best_row = None

    for _, row in faq_df.iterrows():
        faq_q = str(row["Question"]).strip().lower()
        
        score_ratio = fuzz.ratio(clean_query, faq_q)
        score_sort = fuzz.token_sort_ratio(clean_query, faq_q)
        score_set = fuzz.token_set_ratio(clean_query, faq_q)
        
        if len(clean_query.split()) >= 2 and len(clean_query) >= 8:
            score_partial = fuzz.partial_ratio(clean_query, faq_q)
            combined_score = max(score_ratio, score_sort, score_set, score_partial)
        else:
            combined_score = max(score_ratio, score_sort, score_set)

        if combined_score > best_score:
            best_score = combined_score
            best_row = row

    is_match = best_score >= threshold
    return best_row, round(best_score, 1), is_match


# ==========================================
# SMART AI ENGINE & ESCALATION LOGIC
# ==========================================
def get_active_api_key() -> str | None:
    """
    Retrieve Gemini API key safely from:
    1. Session state (UI input)
    2. Streamlit secrets (.streamlit/secrets.toml)
    3. OS Environment variables
    """
    # 1. Check UI Session State
    if st.session_state.get("gemini_api_key"):
        return st.session_state["gemini_api_key"].strip()

    # 2. Check Streamlit Secrets
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
        if "GOOGLE_API_KEY" in st.secrets:
            return str(st.secrets["GOOGLE_API_KEY"]).strip()
    except Exception:
        pass

    # 3. Check Environment Variables
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if env_key:
        return env_key.strip()

    return None


def classify_and_generate_offline(query: str, faq_df: pd.DataFrame) -> tuple[str, str]:
    """
    Intelligent offline assistant when no Gemini API key is configured.
    Answers general/conversational questions and escalates company-specific inquiries.
    """
    q_lower = query.strip().lower()

    # Inquiries that strictly require official company human support
    escalation_triggers = [
        "tokyo", "physical store", "retail store", "branch", "headquarters", "address", "location",
        "job", "hiring", "career", "internship", "vacancy", "resume",
        "order #", "order number", "my order id", "track #",
        "custom discount", "wholesale price", "quote", "bulk contract",
        "complaint", "legal", "lawsuit", "manager", "ceo", "director", "owner", "price match"
    ]
    if any(trigger in q_lower for trigger in escalation_triggers):
        return ("This inquiry involves specific company operations, policies, or locations not covered in public FAQs.", "ESCALATE")

    # Conversational greetings
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings"]
    if any(q_lower == g or q_lower.startswith(g + " ") for g in greetings):
        return ("Hello! 👋 I am your automated AI support assistant. I can help answer common questions about our store policies, business hours, payment options, and general shopping guidance. How may I assist you today?", "AI")

    # Closing / Gratitude
    thanks = ["thank you", "thanks", "appreciate it", "bye", "goodbye"]
    if any(t in q_lower for t in thanks):
        return ("You're very welcome! Feel free to ask anytime if you need more assistance. Have a wonderful day! 😊", "AI")

    # General eCommerce and shopping concepts
    if "online shopping" in q_lower or "how it works" in q_lower:
        return ("Online shopping allows you to browse products, add items to your digital cart, proceed through secure checkout, and receive items delivered directly to your doorstep. You can track your shipment in real time once dispatched.", "AI")

    if "business day" in q_lower:
        return ("A 'business day' typically refers to standard working days (Monday through Friday), excluding weekends and official public holidays. Shipping estimates are usually calculated in business days.", "AI")
    
    if "invoice" in q_lower:
        return ("An invoice is an itemized commercial document that records the products or services delivered to a customer, total amount due, taxes, and payment terms.", "AI")

    if "sizing" in q_lower or "size" in q_lower:
        return ("For best sizing results when shopping online, we recommend measuring your bust/chest, waist, and hips with a flexible measuring tape and comparing them with the sizing guide on the product page.", "AI")

    if "secure" in q_lower or "safety" in q_lower or "encrypt" in q_lower:
        return ("Modern eCommerce transactions use 256-bit SSL encryption and strict PCI-DSS compliance to ensure payment credentials and personal data remain protected.", "AI")

    # Safe default: Escalate to support if unknown and unverified
    return ("This question requires specific company verification from our support team.", "ESCALATE")


def generate_ai_response(query: str, faq_df: pd.DataFrame, api_key: str | None = None) -> tuple[str, str]:
    """
    Step 2 & 3: Use an AI model to answer general questions intelligently.
    If official company-specific information is requested or uncertain, signals escalation.
    Returns (response_text, "AI" | "ESCALATE").
    """
    clean_api_key = (api_key or "").strip()

    if clean_api_key:
        try:
            from google import genai
            client = genai.Client(api_key=clean_api_key)

            faqs_summary = "\n".join(
                f"- Q: {row['Question']} | A: {row['Answer']}"
                for _, row in faq_df.head(20).iterrows()
            )

            prompt = f"""You are an intelligent, polite, and responsible customer support AI assistant for a business.
Here is the list of official verified company FAQs:
{faqs_summary}

The customer asked: "{query}"

Strict Operating Rules:
1. If the question is a general greeting, polite conversation, general ecommerce concept, sizing advice, or general online shopping advice, provide a concise, friendly, and helpful answer.
2. If the question requires official company-specific information NOT available in the verified FAQs above (such as physical retail store branches, employee contact details, personalized order tracking for specific order numbers, job applications, custom commercial pricing, or specific legal policies), DO NOT GUESS OR INVENT POLICIES.
Instead, your response MUST begin with the exact word:
[ESCALATE]
followed by a one-sentence reason why official human support is required.
3. NEVER invent or hallucinate company policies, prices, refund rules, physical store addresses, or staff names.
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = (response.text or "").strip()

            if text.startswith("[ESCALATE]"):
                reason = text.replace("[ESCALATE]", "").strip()
                return (reason, "ESCALATE")
            elif text:
                return (text, "AI")
        except Exception as e:
            # Fall back to offline assistant if Gemini API call fails (e.g. invalid key or network issue)
            pass

    return classify_and_generate_offline(query, faq_df)


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! 👋 Welcome to Smart Customer Support. I am your automated AI assistant.\n\nI can answer questions about our business hours, return policy, payment methods, shipping, or assist with general shopping guidance. If you ask something that requires human verification, I will forward your inquiry with a unique Ticket ID!",
            "time": datetime.now().strftime("%I:%M %p"),
            "source": "GREETING",
            "escalated": False,
        }
    ]

if "prefilled_prompt" not in st.session_state:
    st.session_state.prefilled_prompt = ""

if "track_ticket_input" not in st.session_state:
    st.session_state.track_ticket_input = ""

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

# Load datasets and ticket stats
faq_df = load_faq_data()
stats = get_ticket_counts()
active_key = get_active_api_key()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 🤖 SupportDesk AI")
    st.caption("College Mini Project • Smart FAQ & Ticket Portal")
    st.divider()

    # AI Model Status
    st.markdown("#### ⚡ AI Engine Status")
    if active_key:
        st.success("🟢 Gemini AI: Active (Live Model)")
    else:
        st.info("🟡 Gemini AI: Smart Offline Mode")

    with st.expander("🔑 Configure Gemini API Key"):
        st.caption("Enter your Google Gemini API key to enable live Gemini 2.5 Flash responses:")
        input_key = st.text_input(
            "Gemini API Key:",
            type="password",
            value=st.session_state.gemini_api_key,
            placeholder="AIzaSy...",
            help="Your key is stored safely in session state and is never hardcoded."
        )
        if st.button("Save API Key in Session", use_container_width=True):
            st.session_state.gemini_api_key = input_key.strip()
            st.success("API Key updated for this session!")
            st.rerun()

    st.divider()

    # Metric summary in sidebar
    st.markdown("#### 📈 Support Metrics")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric(label="FAQs Loaded", value=len(faq_df))
    with col_sb2:
        st.metric(label="Total Tickets", value=stats["total"])

    col_sb3, col_sb4 = st.columns(2)
    with col_sb3:
        st.metric(label="⏳ Pending", value=stats["pending"])
    with col_sb4:
        st.metric(label="✅ Resolved", value=stats["resolved"])

    st.divider()

    # Matching Sensitivity Slider
    st.markdown("#### ⚙️ FAQ Search Sensitivity")
    threshold = st.slider(
        "FAQ Match Threshold (%)",
        min_value=50,
        max_value=95,
        value=68,
        step=1,
        help="Questions scoring above this similarity percentage use the exact FAQ answer. Below this, questions are routed to AI.",
    )

    st.divider()

    # Quick Test Questions
    st.markdown("#### 💡 Test Scenarios")
    st.caption("Click any question to test:")
    
    test_scenarios = [
        ("What are your business hours?", "FAQ"),
        ("What payment methods do you accept?", "FAQ"),
        ("What is an invoice and why is it needed?", "AI"),
        ("What are business days in shipping?", "AI"),
        ("Do you have a physical store in Tokyo?", "ESCALATE"),
        ("Can I apply for a job or internship?", "ESCALATE"),
    ]

    for sq, category in test_scenarios:
        if category == "FAQ":
            badge = "📋 [FAQ]"
        elif category == "AI":
            badge = "✨ [AI]"
        else:
            badge = "⚠️ [Escalate]"
            
        label = f"{badge} {sq}"
        if st.button(label, key=f"btn_{sq}", use_container_width=True):
            st.session_state.prefilled_prompt = sq

    st.divider()

    # Clear Chat Button
    if st.button("🧹 Clear Chat History", use_container_width=True, type="secondary"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chat history cleared. How can I assist you today?",
                "time": datetime.now().strftime("%I:%M %p"),
                "source": "GREETING",
                "escalated": False,
            }
        ]
        st.rerun()

    st.caption("Python • Streamlit • SQLite • RapidFuzz • Gemini AI")

# ==========================================
# MAIN APPLICATION INTERFACE
# ==========================================
st.markdown(
    """
    <div class="main-header">
        <h1>🤖 AI-Powered Customer Support & Support Tickets</h1>
        <p>1. Search Verified FAQs &nbsp;•&nbsp; 2. Smart AI Answer for General Questions &nbsp;•&nbsp; 3. Escalation for Official Support</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Navigation tabs
tab_chat, tab_track, tab_admin, tab_faqs = st.tabs([
    "💬 Customer Support Chat",
    "🔍 Customer Ticket Tracking",
    "🛡️ Admin Escalation Dashboard",
    "📚 FAQ Knowledge Base",
])

# ------------------------------------------
# TAB 1: CUSTOMER SUPPORT CHAT
# ------------------------------------------
with tab_chat:
    # Top KPI summary bar
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.markdown(
            f"""
            <div class="metric-card total">
                <div class="metric-title">Available FAQs</div>
                <div class="metric-value">{len(faq_df)} Questions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_kpi2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">Total Tickets</div>
                <div class="metric-value">{stats["total"]} Inquiries</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_kpi3:
        st.markdown(
            f"""
            <div class="metric-card pending">
                <div class="metric-title">Pending Tickets</div>
                <div class="metric-value">{stats["pending"]} Awaiting</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_kpi4:
        st.markdown(
            f"""
            <div class="metric-card resolved">
                <div class="metric-title">Resolved Tickets</div>
                <div class="metric-value">{stats["resolved"]} Solved</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Display chat conversation history
    for msg in st.session_state.messages:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            if msg.get("escalated"):
                # Escalated case
                st.markdown('<span class="escalate-badge">⚠️ Escalated to Support Team</span>', unsafe_allow_html=True)
                if msg.get("ticket_id"):
                    st.markdown(f'<span class="ticket-badge">Ticket: {msg["ticket_id"]}</span>', unsafe_allow_html=True)
                st.error(msg["content"])
                if msg.get("ticket_note"):
                    st.info(msg["ticket_note"])
            else:
                if msg["role"] == "assistant":
                    # Distinct badges for FAQ vs AI
                    if msg.get("source") == "FAQ":
                        st.markdown(
                            f'<span class="matched-badge">✓ Verified FAQ Answer ("{msg.get("matched_faq")}" — {msg.get("confidence")}%)</span>',
                            unsafe_allow_html=True,
                        )
                    elif msg.get("source") == "AI":
                        st.markdown(
                            '<span class="ai-badge">✨ AI-Generated Guidance (General Knowledge)</span>',
                            unsafe_allow_html=True,
                        )
                st.markdown(msg["content"])
            if "time" in msg:
                st.markdown(f'<div class="chat-timestamp">{msg["time"]}</div>', unsafe_allow_html=True)

    # Chat Input handler
    user_input = st.chat_input("Type your question here (e.g., 'What is your return policy?' or 'What are business days?')...")
    
    # Check if a sample question was clicked
    if not user_input and st.session_state.prefilled_prompt:
        user_input = st.session_state.prefilled_prompt
        st.session_state.prefilled_prompt = ""

    if user_input:
        current_time = datetime.now().strftime("%I:%M %p")
        
        # 1. Append User Message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "time": current_time,
            "escalated": False,
        })
        
        # STEP 1: Search the existing FAQ CSV FIRST for every customer question
        best_match, score, is_match = find_best_faq_match(user_input, faq_df, threshold=threshold)

        if is_match and best_match is not None:
            # STEP 2: Exact FAQ answer found -> display verified answer
            bot_reply = str(best_match["Answer"])
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_reply,
                "time": current_time,
                "source": "FAQ",
                "matched_faq": str(best_match["Question"]),
                "confidence": score,
                "escalated": False,
            })
        else:
            # STEP 3 & 4: No FAQ match found -> Use AI Model to generate helpful answer
            # Do NOT automatically escalate every unknown FAQ question
            ai_reply, response_type = generate_ai_response(user_input, faq_df, api_key=active_key)

            if response_type == "AI":
                # STEP 5: Answer general questions intelligently using AI
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_reply,
                    "time": current_time,
                    "source": "AI",
                    "confidence": None,
                    "escalated": False,
                })
            else:
                # STEP 6: Requires official company-specific info, uncertain, or policy -> ESCALATE
                exact_escalation_reply = "ESCALATE: Your question has been forwarded to our support team."
                
                # Save into SQLite and sync with CSV
                ticket_id, is_new = create_or_get_ticket(user_input)
                
                ticket_note = (
                    f"🎫 **Ticket ID: `{ticket_id}`** (Status: **Pending**)\n\n"
                    f"This question requires official company-specific verification. "
                    f"You can check our team's response anytime under the **'🔍 Customer Ticket Tracking'** tab using your Ticket ID."
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": exact_escalation_reply,
                    "time": current_time,
                    "source": "ESCALATE",
                    "escalated": True,
                    "ticket_id": ticket_id,
                    "ticket_note": ticket_note,
                })

        st.rerun()

# ------------------------------------------
# TAB 2: CUSTOMER TICKET TRACKING
# ------------------------------------------
with tab_track:
    st.subheader("🔍 Track Your Support Ticket")
    st.caption("Check the live status and read replies from our customer support team.")

    col_track_in, col_track_btn = st.columns([3, 1])
    with col_track_in:
        track_id_query = st.text_input(
            "Enter your Ticket ID:",
            value=st.session_state.track_ticket_input,
            placeholder="e.g., TCK-1001",
            help="Ticket IDs are provided when your question is escalated.",
        )
    with col_track_btn:
        st.write("")
        st.write("")
        track_submitted = st.button("🔎 Check Status", use_container_width=True, type="primary")

    if track_submitted or track_id_query.strip():
        search_id = track_id_query.strip()
        ticket_info = get_ticket_by_id(search_id)

        if ticket_info:
            status_val = ticket_info["status"]
            is_resolved = (status_val == "Resolved")

            status_color = "#10B981" if is_resolved else "#F59E0B"
            status_label = "✅ Resolved" if is_resolved else "⏳ Pending Review"

            st.markdown(
                f"""
                <div class="ticket-display-box">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 16px;">
                        <div>
                            <span style="font-size: 13px; color: #64748B; font-weight: 600;">TICKET ID</span>
                            <h2 style="margin: 0; color: #1E3A8A; font-size: 22px;">{ticket_info['ticket_id']}</h2>
                        </div>
                        <div style="background-color: {status_color}20; color: {status_color}; font-weight: 700; font-size: 14px; padding: 6px 14px; border-radius: 9999px;">
                            {status_label}
                        </div>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <span style="font-size: 12px; color: #64748B; font-weight: 600; text-transform: uppercase;">Your Question:</span>
                        <p style="font-size: 16px; color: #0F172A; font-weight: 500; margin: 4px 0;">{ticket_info['customer_question']}</p>
                        <span style="font-size: 12px; color: #94A3B8;">Submitted on: {ticket_info['date_time']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if is_resolved:
                st.markdown(
                    f"""
                    <div class="reply-box">
                        <div style="font-weight: 700; color: #166534; font-size: 14px; margin-bottom: 6px;">
                            💬 Official Support Reply:
                        </div>
                        <div style="font-size: 15px; color: #14532D; line-height: 1.5;">
                            {ticket_info['admin_reply']}
                        </div>
                        <div style="font-size: 11px; color: #15803D; margin-top: 8px;">
                            Replied at: {ticket_info['reply_time']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div class="pending-box">
                        <div style="font-weight: 700; color: #92400E; font-size: 14px; margin-bottom: 4px;">
                            ⏳ Status: Pending Review
                        </div>
                        <div style="font-size: 14px; color: #78350F;">
                            Our customer support team has received your inquiry and is currently reviewing it. Please check back shortly for our official reply!
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            if search_id:
                st.warning(f"❌ No ticket found with ID: **'{search_id}'**. Please verify the Ticket ID and try again.")

# ------------------------------------------
# TAB 3: ADMIN ESCALATION DASHBOARD & REPLY
# ------------------------------------------
with tab_admin:
    st.subheader("🛡️ Support Escalation Portal & Admin Replies")
    st.caption("Review escalated customer tickets, write official replies, and mark tickets as resolved.")

    # Refresh tickets and stats
    tickets_df = get_all_tickets()
    current_stats = get_ticket_counts()

    # KPI metric cards
    col_adm1, col_adm2, col_adm3 = st.columns(3)
    with col_adm1:
        st.markdown(
            f"""
            <div class="metric-card total">
                <div class="metric-title">Total Escalated Tickets</div>
                <div class="metric-value">{current_stats['total']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_adm2:
        st.markdown(
            f"""
            <div class="metric-card pending">
                <div class="metric-title">Pending Action</div>
                <div class="metric-value">{current_stats['pending']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_adm3:
        st.markdown(
            f"""
            <div class="metric-card resolved">
                <div class="metric-title">Resolved Tickets</div>
                <div class="metric-value">{current_stats['resolved']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Download CSV button
    if not tickets_df.empty:
        csv_download = tickets_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download escalated_questions.csv",
            data=csv_download,
            file_name="escalated_questions.csv",
            mime="text/csv",
            type="secondary",
        )

    st.divider()

    # Section 1: Admin Reply System
    st.markdown("### ✉️ Support Team Reply Console")
    
    pending_tickets = tickets_df[tickets_df["status"] == "Pending"]
    
    if pending_tickets.empty:
        st.success("🎉 All caught up! There are currently no pending tickets requiring a reply.")
    else:
        ticket_options = {
            f"{row['ticket_id']} — {row['customer_question'][:45]}... ({row['date_time']})": row['ticket_id']
            for _, row in pending_tickets.iterrows()
        }

        selected_ticket_label = st.selectbox(
            "Select a Pending Ticket to Answer:",
            options=list(ticket_options.keys()),
            help="Choose the ticket you want to answer and resolve.",
        )

        selected_id = ticket_options[selected_ticket_label]
        selected_record = get_ticket_by_id(selected_id)

        if selected_record:
            st.markdown(
                f"""
                <div style="background: white; border: 1px solid #CBD5E1; border-radius: 8px; padding: 14px 18px; margin: 12px 0;">
                    <span style="font-size: 11px; font-weight: 700; color: #2563EB;">SELECTED TICKET: {selected_record['ticket_id']}</span>
                    <p style="font-size: 15px; font-weight: 600; color: #1E293B; margin: 4px 0 2px 0;">
                        Question: "{selected_record['customer_question']}"
                    </p>
                    <span style="font-size: 12px; color: #64748B;">Received: {selected_record['date_time']}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("admin_reply_form", clear_on_submit=True):
                admin_reply_text = st.text_area(
                    "Write Your Official Response:",
                    placeholder="Type the solution or answer for the customer here...",
                    height=120,
                )
                submit_reply = st.form_submit_button("✉️ Submit Reply & Mark as Resolved", type="primary")

                if submit_reply:
                    if admin_reply_text.strip():
                        success = submit_admin_reply(selected_id, admin_reply_text)
                        if success:
                            st.success(f"✅ Reply successfully submitted for Ticket {selected_id}! Status changed to 'Resolved'.")
                            st.rerun()
                    else:
                        st.error("Please enter a reply before submitting.")

    st.divider()

    # Section 2: All Tickets Data Table with Filter
    st.markdown("### 📋 All Escalated Tickets (SQLite Database)")

    if tickets_df.empty:
        st.info("No tickets recorded yet.")
    else:
        col_filt1, col_filt2 = st.columns([1, 2])
        with col_filt1:
            status_filter = st.selectbox("Filter by Status:", ["All", "Pending", "Resolved"])
        with col_filt2:
            search_ticket_text = st.text_input("Search tickets:", placeholder="Search by Ticket ID or keywords...")

        filtered_df = tickets_df.copy()
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["status"] == status_filter]
        if search_ticket_text.strip():
            kw = search_ticket_text.strip()
            filtered_df = filtered_df[
                filtered_df["ticket_id"].astype(str).str.contains(kw, case=False, na=False)
                | filtered_df["customer_question"].astype(str).str.contains(kw, case=False, na=False)
                | filtered_df["admin_reply"].astype(str).str.contains(kw, case=False, na=False)
            ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "ticket_id": st.column_config.TextColumn("Ticket ID", width="small"),
                "customer_question": st.column_config.TextColumn("Customer Question", width="large"),
                "date_time": st.column_config.TextColumn("Date & Time", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "admin_reply": st.column_config.TextColumn("Admin Reply", width="large"),
                "reply_time": st.column_config.TextColumn("Reply Time", width="medium"),
            },
            hide_index=True,
        )

# ------------------------------------------
# TAB 4: FAQ KNOWLEDGE BASE
# ------------------------------------------
with tab_faqs:
    st.subheader("📚 Loaded Knowledge Base (FAQ.csv)")
    st.caption("These are the questions and answers currently loaded into the chatbot's memory.")

    faq_search = st.text_input("🔍 Search FAQs:", placeholder="Type to filter questions...")
    filtered_faq = faq_df
    if faq_search.strip():
        filtered_faq = filtered_faq[
            filtered_faq["Question"].astype(str).str.contains(faq_search.strip(), case=False, na=False)
            | filtered_faq["Answer"].astype(str).str.contains(faq_search.strip(), case=False, na=False)
        ]

    st.dataframe(
        filtered_faq,
        use_container_width=True,
        column_config={
            "Question": st.column_config.TextColumn("FAQ Question", width="medium"),
            "Answer": st.column_config.TextColumn("FAQ Answer", width="large"),
        },
        hide_index=True,
    )

    st.divider()

    with st.expander("➕ Add New Question & Answer to FAQ.csv"):
        with st.form("add_faq_form"):
            new_question = st.text_input("New Question:")
            new_answer = st.text_area("Answer:")
            submitted = st.form_submit_button("Add to FAQ.csv")

            if submitted:
                if new_question.strip() and new_answer.strip():
                    new_row = pd.DataFrame([{"Question": new_question.strip(), "Answer": new_answer.strip()}])
                    updated_faq = pd.concat([faq_df, new_row], ignore_index=True)
                    updated_faq.to_csv(FAQ_FILE, index=False)
                    st.success(f"Added new FAQ: '{new_question}'")
                    st.rerun()
                else:
                    st.error("Please fill in both the Question and the Answer fields.")
