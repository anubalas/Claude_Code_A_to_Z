import sys
import json
import requests


def main():
    try:
        data = json.load(sys.stdin)

        # Claude Code hook payload may not always use the same field.
        # Prefer actual user input if present.
        prompt = (
            data.get("input")
            or data.get("prompt")
            or data.get("user_input")
            or ""
        )

        # Debug log to stderr so it does not interfere with hook JSON output
        print(f"HOOK RECEIVED PROMPT: {repr(prompt)}", file=sys.stderr)

        if not prompt.strip():
            # No prompt found, allow instead of breaking the flow
            sys.exit(0)

        response = requests.post(
            "http://localhost:8000/guarded_chat",
            json={"prompt": prompt},
            timeout=120
        )
        response.raise_for_status()

        result = response.json()

        print(f"HOOK API RESPONSE: {result}", file=sys.stderr)

        if result.get("blocked") is True:
            print(json.dumps({
                "decision": "block",
                "reason": "Blocked by ENTERPRISE GUARDRAIL POLICY",
                "continue": False
            }))
            sys.exit(2)

        # Allowed
        sys.exit(0)

    except requests.RequestException as e:
        print(f"HOOK REQUEST ERROR: {str(e)}", file=sys.stderr)
        # Fail open for now. Change to sys.exit(2) if you want fail-closed behavior.
        sys.exit(0)

    except Exception as e:
        print(f"HOOK GENERAL ERROR: {str(e)}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()