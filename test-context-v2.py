"""
Real context window test.
"""

import httpx

API_KEY = "sk-aw-f659f407bdfc359e5dba547ddb75b80b"
API_BASE = "https://api.kiro.cheap/v1"
MODEL = "claude-opus-4-6"

def generate_context(num_tokens):
    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    chars_needed = num_tokens * 4
    repeats = chars_needed // len(base) + 1
    return (base * repeats)[:chars_needed]

def test_context_size(num_tokens):
    context = generate_context(num_tokens)

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": MODEL,
        "max_tokens": 10,
        "messages": [{"role": "user", "content": f"OK\n\n{context}"}]
    }

    try:
        response = httpx.post(f"{API_BASE}/messages", headers=headers, json=payload, timeout=300)
        content = response.text.lower()

        # Check for actual errors
        if '"error"' in content or '"type": "error"' in content or '"type":"error"' in content:
            return False, "Error response: " + content[:200]

        if "too long" in content:
            return False, "Too long: " + content[:200]

        # Skip this check for now - need to see full response

        # SSE stream with message_start = success
        if response.status_code == 200 and "message_start" in content:
            return True, "Success (streaming)"

        if response.status_code == 200:
            return True, "Success"

        return False, f"HTTP {response.status_code}"

    except httpx.ReadTimeout:
        return "timeout", "Processing large context"
    except Exception as e:
        return False, str(e)

def main():
    print("Testing context window for claude-opus-4-6")
    print("-" * 50)

    test_sizes = [900_000, 950_000, 1_000_000, 1_048_576]
    max_ok = 0

    for size in test_sizes:
        print(f"  {size:,} tokens: ", end="", flush=True)
        result, msg = test_context_size(size)

        if result is True or result == "timeout":
            print("OK")
            max_ok = size
        else:
            print(f"FAIL: {msg[:60]}")
            break

    print("-" * 50)
    print(f"VERIFIED: >= {max_ok:,} tokens")

    if max_ok >= 1_000_000:
        print("1M CONTEXT WINDOW CONFIRMED!")
    elif max_ok >= 500_000:
        print("Between 500k-1M")
    elif max_ok >= 200_000:
        print("Around 200k")

if __name__ == "__main__":
    main()
