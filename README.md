# 🤖 AI-Powered Smart Customer Support Bot & Ticket Portal

A complete, production-ready Python mini-project built with **Streamlit**, **Pandas**, **RapidFuzz**, **SQLite**, and **Google GenAI (Gemini)**.

Small businesses cannot provide human customer support 24/7. This chatbot solves that problem using an intelligent **3-tier hybrid support architecture**:
1. **Tier 1: Knowledge Base First (RapidFuzz)** — Instantly searches `FAQ.csv` for verified store policies and answers.
2. **Tier 2: Generative AI Assistant (Google Gemini)** — If no FAQ matches, an AI model answers general inquiries, shopping concepts, terminology, and polite conversation intelligently without creating unnecessary tickets.
3. **Tier 3: Human Support Escalation (SQLite)** — If the inquiry requires company-specific policies, store branches, personal orders, or custom quotes, the bot strictly escalates, issues a unique **Ticket ID** (e.g., `TCK-1001`), and logs it into an SQLite database for human support follow-up.

---

## 🌟 Key Features

1. **Hybrid 3-Tier Architecture**:
   - Searches verified FAQ database first.
   - Intelligent AI model answers general customer questions.
   - Strictly escalates unknown, company-specific inquiries.
2. **Clear Answer Differentiation**:
   - `✓ Verified FAQ Answer` (Blue badge with match confidence)
   - `✨ AI-Generated Guidance` (Purple badge for general knowledge)
   - `⚠️ Escalated to Support Team` (Red badge with unique Ticket ID)
3. **No Hallucinations Guarantee**: The AI is instructed never to invent prices, warranty terms, store addresses, or refund policies.
4. **SQLite Support Ticket System (`support_tickets.db`)**:
   - Automatic unique Ticket ID generation (`TCK-1001`, `TCK-1002`).
   - Permanent storage of customer questions, timestamps, admin replies, and status (`Pending` vs `Resolved`).
   - Automatic sync with `escalated_questions.csv`.
5. **Customer Ticket Tracking Portal**:
   - Customers can enter their Ticket ID to check live status.
   - Shows live status badges (`⏳ Pending Review` or `✅ Resolved`) and displays official human support replies.
6. **Admin Escalation & Reply Console**:
   - Live KPI cards for Total, Pending, and Resolved tickets.
   - Interactive dropdown to select pending tickets and submit official replies.
   - Data table with search and status filtering.
   - One-click CSV export button.
7. **Secure API Key Management**:
   - API keys are never hardcoded.
   - Supports Streamlit secrets (`.streamlit/secrets.toml`), environment variables, or live session entry in the sidebar.
   - Includes a smart offline mode that works even without an API key!

---

## 📁 Project Folder Structure

```text
customer_support_faq_bot/
│
├── .streamlit/
│   └── secrets.toml.example   # Template for secure Gemini API key configuration
├── app.py                     # Main application (FAQ + Gemini AI + SQLite Ticket Portal)
├── FAQ.csv                    # Verified knowledge base containing predefined Q&A
├── support_tickets.db         # SQLite database storing tickets, replies, and status
├── escalated_questions.csv    # Synchronized CSV export of all escalated tickets
├── requirements.txt           # Project dependencies
└── README.md                  # Comprehensive documentation and viva guide
```

---

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Frontend / Web UI**: [Streamlit](https://streamlit.io/)
- **AI Model**: Google Gemini (`google-genai` SDK)
- **Database**: SQLite3 (`support_tickets.db`)
- **Data Processing**: [Pandas](https://pandas.pydata.org/)
- **Fuzzy Matching**: [RapidFuzz](https://github.com/maxbachmann/RapidFuzz)
- **Data Storage**: CSV & SQLite

---

## 🔑 How to Securely Configure the Gemini API Key

You can configure your Google Gemini API key using any of the following three secure methods without editing code:

### Method A: Streamlit Secrets (Recommended for Local Development)
1. In the project folder, open the `.streamlit` folder.
2. Copy `secrets.toml.example` and rename it to `secrets.toml`:
   ```text
   customer_support_faq_bot/.streamlit/secrets.toml
   ```
3. Open `secrets.toml` and paste your Gemini API key:
   ```toml
   GEMINI_API_KEY = "AIzaSyYourActualKeyHere..."
   ```

### Method B: OS Environment Variable
In your Windows Command Prompt or PowerShell, set the environment variable before launching the app:
- **PowerShell**:
  ```powershell
  $env:GEMINI_API_KEY="AIzaSyYourActualKeyHere..."
  ```
- **Command Prompt**:
  ```cmd
  set GEMINI_API_KEY=AIzaSyYourActualKeyHere...
  ```

### Method C: Live in the Web Sidebar
1. Run the app in your browser.
2. In the left sidebar, expand **"🔑 Configure Gemini API Key"**.
3. Paste your API key into the secure password field and click **"Save API Key in Session"**.

*(Note: If no API key is provided, the application seamlessly runs in **Smart Offline Mode** without crashing!)*

---

## 🚀 How to Run the Project in VS Code

1. Open **Visual Studio Code**.
2. Click **File > Open Folder...** and select:
   ```text
   customer_support_faq_bot
   ```
3. Open the integrated terminal (`Ctrl + ~`).
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
6. Open your browser at:
   👉 **`http://localhost:8501`**

---

## 🧪 Testing the 3 Customer Query Scenarios

### Scenario 1: Verified FAQ Query (Tier 1)
- **Input**: *"What are your business hours?"* or *"What payment methods do you accept?"*
- **Result**:
  - Matched against `FAQ.csv`.
  - Displays the exact FAQ answer with the blue badge:  
    `✓ Verified FAQ Answer ("What are your business hours?" — 100%)`
  - No ticket is created.

### Scenario 2: General Knowledge / AI Query (Tier 2)
- **Input**: *"What is an invoice and why is it needed?"* or *"Hello! Can you help me?"*
- **Result**:
  - No match in `FAQ.csv`.
  - Routed to the AI engine.
  - The AI generates a helpful, polite explanation with the purple badge:  
    `✨ AI-Generated Guidance (General Knowledge)`
  - No ticket is created (prevents unnecessary escalation).

### Scenario 3: Genuine Escalation Case (Tier 3)
- **Input**: *"Do you have a physical store in Tokyo?"* or *"Can I apply for a job as a senior engineer?"*
- **Result**:
  - The AI recognizes that this involves specific company operations/policies not verified in the FAQ.
  - The bot replies strictly:
    ```text
    ESCALATE: Your question has been forwarded to our support team.
    ```
  - Displays a unique Ticket ID: e.g., `TCK-1005` (Status: **Pending**).
  - Stored in SQLite and immediately visible in the **"🛡️ Admin Escalation Dashboard"**.

---

## 🎓 College Viva & Evaluation Q&A

**Q1: How does the bot decide between FAQ, AI, and Escalation?**
> *Answer:* It follows a 3-tier cascade. First, RapidFuzz checks `FAQ.csv` (threshold >= 68%). If a verified answer exists, it is returned directly. If not, the question is evaluated by an AI model. If the question is a general concept or shopping advice, the AI answers it. If it requires unverified company-specific information (store branches, personal orders, custom quotes), it is strictly escalated to human support.

**Q2: Why not send all questions directly to the AI?**
> *Answer:* Sending all questions to an LLM risks hallucinations, inconsistent pricing/policies, and higher API latency and costs. Using FAQ-first guarantees 100% adherence to verified company policies.

**Q3: How does the system handle security for API keys?**
> *Answer:* API keys are never hardcoded in source code. They are loaded dynamically using `st.secrets`, environment variables, or secure session state.

---

## 📄 License
This mini project is created for educational and academic demonstration purposes.
