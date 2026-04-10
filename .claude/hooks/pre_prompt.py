import sys
import json
import requests

data = json.load(sys.stdin)

prompt = data.get("prompt","")

response = requests.post(
    "http://localhost:8000/guarded_chat",
    json={"prompt":prompt}
)

result=response.json()

if "sorry" in result["response"].lower() or "blocked" in result["response"].lower() or "can't respond" in result["response"].lower():

    print(json.dumps({
        "decision":"block",
        "reason":"Blocked by ENTERPRISE GUARDRAIL POLICY",
        "continue":False
    }))

    sys.exit(2)

sys.exit(0)