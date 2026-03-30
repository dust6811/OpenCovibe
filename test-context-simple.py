#!/usr/bin/env python3
"""Simple context window test - no emoji for Windows compatibility"""

import os
import httpx

API_KEY = "sk-aw-f659f407bdfc359e5dba547ddb75b80b"
API_BASE = "https://api.kiro.cheap/v1"

def test_context(model: str, tokens: int):
    print(f"Testing {model} with ~{tokens:,} tokens...")

    base = "The quick brown fox jumps over the lazy dog. "
    chars_needed = tokens * 4
    repeats = chars_needed // len(base) + 1
    context_text = (base * repeats)[:chars_needed]

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": model,
        "max_tokens": 100,
        "messages": [{"role": "user", "content": f"Reply: OK\n\n{context_text}"}]
    }

    try:
        response = httpx.post(f"{API_BASE}/messages", headers=headers, json=payload, timeout=300)

        if response.status_code == 200:
            data = response.json()
            input_tokens = data.get("usage", {}).get("input_tokens", tokens)
            print(f"  SUCCESS: {input_tokens:,} input tokens")
            return True
        else:
            error = response.json()
            error_msg = error.get("error", {}).get("message", str(error))
            print(f"  ERROR: {error_msg[:150]}")
            return "too long" in error_msg.lower() or "context" in error_msg.lower()
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return None

print("=" * 60)
print("Context Window Test for api.kiro.cheap")
print("=" * 60)

# Test claude-opus-4-6 at different sizes
for size in [100_000, 500_000, 800_000, 1_000_000]:
    result = test_context("claude-opus-4-6", size)
    if result is False:  # Hit limit
        print(f"\n>>> Context window limit found at ~{size:,} tokens")
        break
    print()

print("Test complete!")
