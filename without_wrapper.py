import requests
import os
import time
import getpass

# -----------------------------
# Helper functions
# -----------------------------
def get_str(prompt, allowed=None):
    while True:
        val = input(prompt).strip().upper()
        if not val:
            print("❌ Input cannot be empty")
            continue
        if allowed and any(c not in allowed for c in val):
            print(f"❌ Only characters allowed: {allowed}")
            continue
        return val


def get_int(prompt, min_val=None, max_val=None, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            val = int(val)
            if min_val is not None and val < min_val:
                print(f"❌ Must be ≥ {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"❌ Must be ≤ {max_val}")
                continue
            return val
        except ValueError:
            print("❌ Enter a valid integer")


def get_float(prompt, min_val=None, max_val=None, default=None):
    while True:
        val = input(prompt).strip()
        if val == "" and default is not None:
            return default
        try:
            val = float(val)
            if min_val is not None and val < min_val:
                print(f"❌ Must be ≥ {min_val}")
                continue
            if max_val is not None and val > max_val:
                print(f"❌ Must be ≤ {max_val}")
                continue
            return val
        except ValueError:
            print("❌ Enter a valid number")


# -----------------------------
# NVIDIA API Key
# -----------------------------
api_key = os.getenv("NVIDIA_API_KEY")

if not api_key:
    api_key = getpass.getpass(
        "Enter NVIDIA API key (input hidden): "
    )
    if not api_key:
        raise RuntimeError("NVIDIA API key is required")

# -----------------------------
# Interactive inputs
# -----------------------------
print("\n=== Evo2 DNA Generator ===\n")

sequence = get_str(
    "Enter DNA sequence (A/C/G/T only): ",
    allowed={"A", "C", "G", "T"}
)

num_tokens = get_int(
    "Number of tokens to generate [1–1000] (default 100): ",
    min_val=1,
    max_val=1000,
    default=100
)

temperature = get_float(
    "Temperature [0.0–2.0] (default 1.0): ",
    min_val=0.0,
    max_val=2.0,
    default=1.0
)

top_k = get_int(
    "Top-k sampling [1–20] (default 4): ",
    min_val=1,
    max_val=20,
    default=4
)

retry_delay = get_int(
    "Delay before request in seconds [0–10] (default 2): ",
    min_val=0,
    max_val=10,
    default=2
)

# -----------------------------
# API call
# -----------------------------
print("\n⏳ Sending request...\n")
time.sleep(retry_delay)

url = "https://health.api.nvidia.com/v1/biology/arc/evo2-40b/generate"

payload = {
    "sequence": sequence,
    "num_tokens": num_tokens,
    "temperature": temperature,
    "top_k": top_k,
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers, timeout=60)

# -----------------------------
# Output
# -----------------------------
if response.status_code == 200:
    result = response.json()
    print("✅ Generated DNA:\n")
    print(result["sequence"])
    print(f"\n⏱ Time: {result['elapsed_ms']} ms")
else:
    print(f"❌ Error {response.status_code}")
    print(response.text)
