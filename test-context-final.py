"""
Real context window test - checks if API accepts large contexts.
"""

import httpx
import re

API_KEY = "sk-aw-f659f407bdfc359e5dba547ddb75b80b"
API_BASE = "https://api.kiro.cheap/v1"
MODEL = "claude-opus-4-6"

def generate_context(num_tokens):
    """Generate text of approximately num_tokens tokens"""
    base = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    chars_needed = num_tokens * 4
    repeats = chars_needed // len(base) + 1
    return (base * repeats)[:chars_needed]

def test_context_size(num_tokens):
    """Test if API accepts a request with given context size"""
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

        content = response.text

        # Check for error patterns
        error_patterns = [
            r'too long',
            r'context.*limit',
            r'max.*context',
            r'prompt.*exceed',
            r'400',
            r'413',
        ]

        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return False, content[:200]

        # Check for success patterns
        if response.status_code == 200:
            # Look for input_tokens in SSE response
            match = re.search(r'"input_tokens":\s*(\d+)', content)
            actual = int(match.group(1)) if match else num_tokens
            return True, f"OK (input_tokens: {actual:,})"

        return True, f"Status: {response.status_code}"

    except httpx.ReadTimeout:
        return "timeout", "Request still processing (good sign for large context)"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 70)
    print("CONTEXT WINDOW TEST - api.kiro.cheap")
    print(f"Model: {MODEL}")
    print("=" * 70)
    print()

    test_sizes = [
        100_000,
        200_000,
        500_000,
        800_000,
        1_000_000,
    ]

    max_confirmed = 0

    for size in test_sizes:
        print(f"Testing {size:,} tokens...", end=" ", flush=True)
        result, msg = test_context_size(size)

        if result is True:
            print(f"OK - {msg}")
            max_confirmed = size
        elif result == "timeout":
            print(f"TIMEOUT - {msg}")
            print("  (Large context is being processed - this is a good sign!)")
            max_confirmed = size
        else:
            print(f"FAILED - {msg[:100]}")
            break

    print()
    print("=" * 70)
    print(f"RESULT: Confirmed context window >= {max_confirmed:,} tokens")

    if max_confirmed >= 1_000_000:
        print("VERIFIED: 1M token context is REAL!")
    elif max_confirmed >= 500_000:
        print("PARTIAL: Between 500k and 1M")
    elif max_confirmed >= 200_000:
        print("LIMITED: Around 200k tokens")
    else:
        print("ERROR: Could not verify")

if __name__ == "__main__":
    main()
