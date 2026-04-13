import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from nemoguardrails import RailsConfig, LLMRails
import uvicorn

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("BASE_DIR:", BASE_DIR)

app = FastAPI(title="AI Governance Guardrail API")

config = RailsConfig.from_path(os.path.join(BASE_DIR, "guardrails"))
rails = LLMRails(config, verbose=True)


class GuardrailRequest(BaseModel):
    prompt: str


class GuardrailResponse(BaseModel):
    response: str
    blocked: bool


@app.post("/guarded_chat", response_model=GuardrailResponse)
async def guarded_chat(request: GuardrailRequest):

    print("API invoked")
    print("PROMPT:", request.prompt)

    try:
        # 
        result = await rails.check_async(
            messages=[
                {
                    "role": "user",
                    "content": request.prompt
                }
            ]
        )

        status = str(result.status).upper()
        blocked = "BLOCKED" in status

        print("STATUS:", status)
        print("BLOCKED:", blocked)

        return GuardrailResponse(
            response="BLOCKED" if blocked else "NOT_BLOCKED",
            blocked=blocked
        )

    except Exception as e:
        print("ERROR:", str(e))

        return GuardrailResponse(
            response="BLOCKED",
            blocked=True
        )


if __name__ == "__main__":
    print("#############################")
    print("GUARDRAIL API Server started")
    print("#############################")

    uvicorn.run(app, host="0.0.0.0", port=8000)