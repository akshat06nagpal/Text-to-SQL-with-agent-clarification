import hashlib
import json
import os
import time
from google import genai
from google.genai import types, errors

client = genai.Client()
MODEL = "gemini-3.8-flash"
CACHE_FILE = "llm_cache.json"

def _load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def call_llm(system_prompt, user_text, json_mode=False, max_attempts=2):
    # The key covers everything that affects the answer. If you edit a prompt,
    # the key changes, so you never get a stale cached reply.
    key = hashlib.sha256(
        json.dumps([MODEL, system_prompt, user_text, json_mode]).encode()
    ).hexdigest()
    cache = _load_cache()
    if key in cache:
        return cache[key]

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0,
        response_mime_type="application/json" if json_mode else None,
    )
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=MODEL, contents=user_text, config=config
            )
            text = response.text.strip()
            cache[key] = text          # only successful replies get cached
            _save_cache(cache)
            return text
        except errors.ServerError as e:
            if attempt == max_attempts:
                raise
            wait = 2 ** attempt
            print(f"  Server busy ({e.code}). Retrying in {wait}s...")
            time.sleep(wait)