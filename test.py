import requests

try:
    response = requests.get("https://www.google.com", timeout=5)

    if response.status_code == 200:
        print("✅ Requests are working")
    else:
        print("⚠️ Request sent but got status:", response.status_code)

except Exception as e:
    print("❌ Request failed")
    print(e)