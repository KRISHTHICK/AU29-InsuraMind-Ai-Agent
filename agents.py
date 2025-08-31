import os
import openai
import time
import json

openai.api_key = os.getenv("OPENAI_API_KEY")  # fallback; streamlit app passes key to calls

def call_gpt(api_key, messages, model="gpt-4.1", max_tokens=512, temperature=0.1):
    # Keep this wrapper for easy update if OpenAI python SDK changes
    import openai
    openai.api_key = api_key
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.1
    )
    text = resp["choices"][0]["message"]["content"]
    return text, resp

def policy_agent(api_key, user_input):
    system = """You are a helpful Insurance Policy Assistant. When a user asks about policy coverage, always:
1) Identify the policy type (e.g., auto, home, health) if possible.
2) Return a short summary (2-3 lines) about likely coverage and what to check in the policy document.
3) If uncertain, propose next steps (documents to upload or questions to ask).
Respond in JSON with keys: summary, checks, next_steps, confidence (0-1)."""
    messages = [{"role":"system","content":system},
                {"role":"user","content":user_input}]
    text, resp = call_gpt(api_key, messages)
    # try to parse JSON
    try:
        parsed = json.loads(text)
        summary = parsed.get("summary", text)
        confidence = float(parsed.get("confidence", 0.6))
    except Exception:
        summary = text
        confidence = 0.6
    meta = {"agent":"policy", "confidence":confidence}
    return summary, meta

def claims_agent(api_key, user_input):
    system = """You are a Claims Triage Assistant. Read the user's description of an incident and:
1) Assign a triage level: low, medium, high (based on safety, damage, medical need).
2) Recommend immediate next steps (e.g., emergency services, photos, estimated documentation).
3) Provide an estimated urgency score 0-1.
Return plain text with a short structured block at the end like: [TRIAGE: high] [URGENCY:0.9]."""
    messages = [{"role":"system","content":system},
                {"role":"user","content":user_input}]
    text, resp = call_gpt(api_key, messages)
    # extract triage & urgency heuristically
    triage = "medium"
    urgency = 0.5
    if "[TRIAGE:" in text:
        try:
            end = text.index("]")
            triage = text[text.index("[TRIAGE:")+8:end].strip()
        except:
            pass
    if "URGENCY:" in text:
        try:
            part = text[text.index("URGENCY:")+8:]
            urgency = float(part.split("]")[0])
        except:
            pass
    meta = {"agent":"claims", "triage":triage, "urgency":urgency, "impact_score": urgency}
    return text, meta

def faq_agent(api_key, user_input, snippets=None):
    # Simple fallback retrieval + LLM response
    if snippets is None: snippets = []
    # naive match
    hits = [s for s in snippets if any(w.lower() in s.lower() for w in user_input.split()[:3])]
    system = "You are an insurance FAQ assistant. If relevant snippets are provided, use them to answer the user succinctly."
    user_msg = user_input
    if hits:
        user_msg += "\n\nRelevant snippets:\n" + "\n".join(hits[:6])
    messages = [{"role":"system","content":system},{"role":"user","content":user_msg}]
    text, resp = call_gpt(api_key, messages)
    meta = {"agent":"faq", "snippets_used": len(hits)}
    return text, meta

def general_chat(api_key, user_input):
    system = "You are a general insurance assistant. Be concise and professional."
    messages = [{"role":"system","content":system},{"role":"user","content":user_input}]
    text, resp = call_gpt(api_key, messages)
    # small heuristic impact score
    meta = {"agent":"general", "impact_score":0.5}
    return text, meta
