import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

load_dotenv()

app = FastAPI(title="Text-to-SQL Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    message: str


class QueryResponse(BaseModel):
    answer: str
    error: str | None = None


@app.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest, x_api_key: str = Header(None, alias="X-Api-Key")
):
    try:
        from agent import create_sql_deep_agent

        agent = create_sql_deep_agent()

        result = agent.invoke(
            {"messages": [{"role": "user", "content": request.message}]}
        )

        final_message = result["messages"][-1]
        answer = (
            final_message.content
            if hasattr(final_message, "content")
            else str(final_message)
        )

        return QueryResponse(answer=answer)

    except Exception as e:
        return QueryResponse(answer="", error=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "ok", "message": "Text-to-SQL Agent API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8024)
