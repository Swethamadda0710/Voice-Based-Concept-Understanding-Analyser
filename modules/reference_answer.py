import os
import time

import requests
import streamlit as st



def _setting(name):
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets.get(name)
    except (FileNotFoundError, KeyError):
        return None


def _gemini_request(model, api_key, prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}}
    try:
        timeout = max(10, int(_setting("GEMINI_TIMEOUT_SECONDS") or 60))
    except (TypeError, ValueError):
        timeout = 60
    last_response = None
    for attempt in range(3):
        try:
            response = requests.post(url, params={"key": api_key}, json=payload, timeout=timeout)
        except requests.Timeout as error:
            if attempt == 2:
                raise RuntimeError(f"Gemini timed out after {timeout} seconds. Try again or use a faster model such as 'gemini-2.5-flash'.") from error
            time.sleep(2 ** attempt)
            continue
        except requests.ConnectionError as error:
            if attempt == 2:
                raise RuntimeError("Gemini could not be reached. Check the deployed app's network connection and try again.") from error
            time.sleep(2 ** attempt)
            continue
        last_response = response
        if response.status_code not in {429, 500, 502, 503, 504}:
            break
        if attempt < 2:
            time.sleep(2 ** attempt)
    if last_response is None:
        raise RuntimeError("Gemini did not return a response.")
    if last_response.status_code == 503:
        raise RuntimeError(f"Gemini model '{model}' is unavailable. Set GEMINI_REFERENCE_MODEL = 'gemini-2.5-flash'.")
    last_response.raise_for_status()
    candidates = last_response.json().get("candidates", [])
    return candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip() if candidates else ""


def generate_reference_answer(question, concept, detail="Medium"):
    """Return an editable AI draft; the caller must approve it before saving."""
    prompt = (
        f"Create a {detail.lower()} educational reference answer for this question: {question}\n"
        f"Concept: {concept}\nUse clear language and include the important concepts needed for semantic comparison."
    )
    gemini_key = _setting("GEMINI_API_KEY")
    if gemini_key:
        configured_model = _setting("GEMINI_REFERENCE_MODEL")
        models = [configured_model, "gemini-2.5-flash"] if configured_model else ["gemini-2.5-flash"]
        content = ""
        for model in dict.fromkeys(models):
            try:
                content = _gemini_request(model, gemini_key, prompt)
                break
            except RuntimeError:
                if model == models[-1]:
                    raise
    else:
        openai_key = _setting("OPENAI_API_KEY")
        if not openai_key:
            raise RuntimeError("Set GEMINI_API_KEY in .streamlit/secrets.toml or as an environment variable.")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
            json={"model": _setting("OPENAI_REFERENCE_MODEL") or "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2},
            timeout=60,
        )
        response.raise_for_status()
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError("The AI returned an empty reference answer.")
    return content
