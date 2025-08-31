# AU29-InsuraMind-Ai-Agent
Ai Agent

# InsureMind - Demo insurance chatbot + agents

## Setup
1. Clone the repo.
2. Create a venv and install dependencies:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

3. Set your OpenAI API key:
   export OPENAI_API_KEY="sk-..."

4. Run:
   streamlit run streamlit_app.py

## Notes
- The app is a demo. For production, add authentication, encrypted storage for PII, logging, and replace the simple retrieval with embeddings+vector DB.
