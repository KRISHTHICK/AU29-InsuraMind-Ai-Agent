import os
import time
import streamlit as st
from agents import policy_agent, claims_agent, faq_agent, general_chat
from utils import timed_call, simple_retrieval, init_state

st.set_page_config(page_title="InsureAI Chatbot", layout="wide")
st.title("InsureAI — Insurance AI Agents & Chatbot (Demo)")

# Sidebar: API key (for demo convenience)
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
use_env = st.sidebar.checkbox("Use env OPENAI_API_KEY", value=bool(os.getenv("OPENAI_API_KEY")))
if use_env and os.getenv("OPENAI_API_KEY"):
    api_key = os.getenv("OPENAI_API_KEY")

agent_choice = st.sidebar.selectbox("Agent", ["General Chat", "Policy Assistant", "Claims Triage", "FAQ Bot"])
show_metrics = st.sidebar.checkbox("Show Real-time Impact Dashboard", True)

# Initialize session state
init_state()

if not api_key:
    st.warning("Enter your OpenAI API key in the sidebar to enable the GPT-4.1 agent.")
    st.stop()

# Simple chat input
with st.form("chat_form", clear_on_submit=False):
    user_text = st.text_area("User message", height=120)
    uploaded = st.file_uploader("Upload FAQ/Policy snippets (optional .txt)", type=["txt"])
    submitted = st.form_submit_button("Send")

if submitted and user_text.strip():
    # Add uploaded snippets to in-memory store
    snippets = []
    if uploaded:
        text = uploaded.read().decode("utf-8")
        snippets = [line.strip() for line in text.splitlines() if line.strip()]
        st.session_state["snippets"].extend(snippets)

    # Choose agent
    if agent_choice == "Policy Assistant":
        func = policy_agent
    elif agent_choice == "Claims Triage":
        func = claims_agent
    elif agent_choice == "FAQ Bot":
        func = lambda *a, **k: faq_agent(*a, snippets=st.session_state["snippets"], **k)
    else:
        func = general_chat

    # Call agent with timing
    response, meta = timed_call(func, api_key=api_key, user_input=user_text)
    st.session_state["conversations"].append({"prompt": user_text, "response": response, "meta": meta})
    st.success("Response received")

# Display last responses
st.subheader("Conversation (latest first)")
for c in reversed(st.session_state["conversations"][-6:]):
    st.markdown(f"**User:** {c['prompt']}")
    st.markdown(f"**Agent:** {c['response']}")
    st.caption(f"Latency: {c['meta'].get('latency', 'n/a')}s  |  Agent: {c['meta'].get('agent','unknown')}")

# Simple "real-time impact" dashboard
if show_metrics:
    st.sidebar.markdown("### Metrics")
    total = len(st.session_state["conversations"])
    avg_latency = sum([c["meta"].get("latency", 0) for c in st.session_state["conversations"]]) / max(1, total)
    st.sidebar.metric("Conversations handled", total)
    st.sidebar.metric("Avg latency (s)", f"{avg_latency:.2f}")

    st.subheader("Impact Summary")
    st.write("- Conversations handled:", total)
    st.write("- Average latency (s):", f"{avg_latency:.2f}")
    # Impact score (heuristic)
    impact_scores = [c["meta"].get("impact_score", 0.5) for c in st.session_state["conversations"]]
    est_impact = sum(impact_scores)/max(1,len(impact_scores))
    st.progress(min(1.0, est_impact))
    st.caption("Progress bar: heuristic estimate of average 'impact' based on agent confidence & triage severity.")
