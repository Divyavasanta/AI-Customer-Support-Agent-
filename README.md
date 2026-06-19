🛍️ AI Customer Support Refund Agent
A high-performance, voice-enabled AI agent designed for e-commerce support, built to handle refund requests, order tracking, and policy enforcement with high accuracy.

🚀 Key Features
Agentic Orchestration: Uses LangGraph and Llama-3 to intelligently route queries between CRM lookups and policy validation.

Voice-First Interaction: Integrated Whisper-large-v3 for real-time, low-latency speech-to-text transcription.

CRM & Policy Engine: SQLite-powered database for order management and a dynamic policy parser.

Admin Observability: Real-time logging panel to monitor the agent’s internal reasoning and tool-calling sequence.

Robust Error Handling: Built-in failsafes to handle edge cases (e.g., human-agent requests) without backend crashes.

🛠️ Tech Stack
Backend: FastAPI, LangGraph, LangChain, SQLite.

LLM/AI: Groq API (Llama-3.3-70b-versatile), Whisper-large-v3.

Frontend: Streamlit (Custom Aesthetic UI).

📂 Project Structure
Plaintext
.
├── app.py           # Streamlit Frontend (with aesthetic CSS)
├── main.py          # FastAPI Backend + LangGraph Agent Logic
├── crm.db           # SQLite database with mock customer profiles
├── policy.md        # Company refund policy rules
└── requirements.txt # Project dependencies
🎥 Loom Video Walkthrough
[INSERT YOUR LOOM VIDEO LINK HERE]

🛠️ Local Setup
Clone the repo:

Bash
git clone <YOUR_REPO_URL>
Setup environment:
Create a .env file and add your GROQ_API_KEY.

Install dependencies:

Bash
pip install -r requirements.txt
Run Backend:

Bash
uvicorn main:app --reload
Run Frontend:

Bash
streamlit run app.py
