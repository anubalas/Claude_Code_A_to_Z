

import os
from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print("BASE_DIR:", BASE_DIR)


# Create FastAPI app
app = FastAPI(title="AI Governance Guardrail API")

# Load guardrails config
config = RailsConfig.from_path(os.path.join(BASE_DIR, "guardrails"))

# Initialize guardrails engine
rails = LLMRails(config, verbose=True)


# Request schema
class GuardrailRequest(BaseModel):
    prompt: str


# Response schema
class GuardrailResponse(BaseModel):
    response: str


# API ENDPOINT
@app.post("/guarded_chat", response_model=GuardrailResponse)
async def guarded_chat(request: GuardrailRequest):

    print("API invoked")

    try:

        response = await rails.generate_async(
            messages=[
                {
                    "role": "user",
                    "content": request.prompt
                }
            ]
        )

        explain = rails.explain()
        explain.print_llm_calls_summary()

        if isinstance(response, dict):

            return GuardrailResponse(
                response=response.get("content", str(response))
            )

        return GuardrailResponse(
            response=str(response)
        )

    except Exception as e:

        return GuardrailResponse(
            response=f"Guardrail error: {str(e)}"
        )


# Start server
if __name__ == "__main__":

    # print("API BASE:", os.getenv("OPENAI_API_BASE"))
    # print("API KEY:", os.getenv("OPENAI_API_KEY")[:10])

    print("#############################")
    print("GUARDRAIL API Server started")
    print("#############################")

    uvicorn.run(app, host="0.0.0.0", port=8000)