"""
Real context window test - sends actual API requests with increasing context sizes.
Tests if api.kiro.cheap really supports 1M tokens for claude-opus-4-6
"""

import httpx
import sys

API_KEY = "sk-aw-f659f407bdfc359e5dba547ddb75b80b"
API_BASE = "https://api.kiro.cheap/v1"
MODEL = "claude-opus-4-6"

def generate_context(num_tokens):
    """Generate text of approximately num_tokens tokens (1 token ~= 4 chars)"""
    base = "The quick brown fox jumps over the lazy dog. "
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
        "max_tokens": 100,
        "messages": [{"role": "user", "content": f"Reply: OK\n\n{context}"}]
    }

    try:
        response = httpx.post(f"{API_BASE}/messages", headers=headers, json=payload, timeout=300)

        print(f"\n      HTTP {response.status_code}")
        print(f"      Response: {response.text[:200]}...")

        if response.status_code == 200:
            data = response.json()
            actual_input = data.get("usage", {}).get("input_tokens", num_tokens)
            return True, actual_input, "OK"
        else:
            try:
                error = response.json()
                msg = error.get("error", {}).get("message", str(error))
            except:
                msg = response.text[:100]
            return False, 0, msg
    except httpx.ReadTimeout:
        return None, 0, "TIMEOUT (request is processing)"
    except Exception as e:
        return False, 0, str(e)

def main():
    print("=" * 70)
    print(f"REAL CONTEXT WINDOW TEST")
    print(f"API: {API_BASE}")
    print(f"Model: {MODEL}")
    print("=" * 70)
    print()

    # Test at key thresholds
    test_sizes = [
        200_000,   # Old Claude limit
        500_000,   # Mid-range
        800_000,   # High
        900_000,   # Very high
        1_000_000, # 1M claim
        1_048_576, # Exact 1M binary
    ]

    results = []

    for size in test_sizes:
        print(f"Testing {size:,} tokens...", end=" ", flush=True)
        success, actual, msg = test_context_size(size)

        if success is True:
            print(f"SUCCESS (actual: {actual:,} tokens)")
            results.append((size, True, actual))
        elif success is None:
            print(f"TIMEOUT - may still be processing")
            results.append((size, None, 0))
        else:
            print(f"FAILED: {msg[:80]}")
            results.append((size, False, msg))
            # Stop at first failure
            break

    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    for size, success, actual in results:
        status = "OK" if success is True else ("TIMEOUT" if success is None else "FAIL")
        if success is True:
            print(f"  {size:,} tokens: {status} (actual input: {actual:,})")
        else:
            print(f"  {size:,} tokens: {status}")

    # Find max confirmed
    confirmed = [r for r in results if r[1] is True]
    if confirmed:
        max_confirmed = max(r[0] for r in confirmed)
        print()
        print(f"CONFIRMED: Context window >= {max_confirmed:,} tokens")

        if max_confirmed >= 1_000_000:
            print("VERIFIED: 1M token context window is REAL!")
        elif max_confirmed >= 500_000:
            print("PARTIAL: More than 200k but less than 1M")
        else:
            print("LIMITED: Context window appears to be around 200k")
    else:
        print()
        print("Could not confirm any context size")

if __name__ == "__main__":
    main()
