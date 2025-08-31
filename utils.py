import time
import streamlit as st

def timed_call(func, *args, **kwargs):
    t0 = time.time()
    try:
        result, meta = func(*args, **kwargs)
    except Exception as e:
        result = f"Error: {e}"
        meta = {"error": str(e)}
    latency = round(time.time() - t0, 2)
    meta.setdefault("latency", latency)
    return result, meta

def init_state():
    if "conversations" not in st.session_state:
        st.session_state["conversations"] = []
    if "snippets" not in st.session_state:
        st.session_state["snippets"] = []
