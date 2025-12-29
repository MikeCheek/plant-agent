from fastapi import FastAPI, HTTPException, Security
from fastapi.params import Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from llm.model import LocalGGUFModel, llm
from app import agent

import os

model = LocalGGUFModel(llm)

app = FastAPI()

API_KEY = os.getenv("API_KEY")

# Define the request structure
class ChatRequest(BaseModel):
    message: str
    reset_history: bool = False

api_key_header = APIKeyHeader(name="X-API-KEY")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post("/chat")
async def chat(request: ChatRequest, api_key: str = Depends(get_api_key)):
  if request.message.strip() == "":
      raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
  try:
      # Run the agent
      response = agent.run(request.message, reset=request.reset_history)
      return {"response": str(response)}
  except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/health")
async def health_check():
    # This only returns 200 OK once the model and agent are fully initialized
    return {"status": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)