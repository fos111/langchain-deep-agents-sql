import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

load_dotenv()

app = FastAPI(title="Text-to-SQL Agent API")


class RunRequest(BaseModel):
    assistant_id: str = "agent"
    input: dict
    stream_mode: str = "updates"


class AssistantConfig(BaseModel):
    assistant_id: str
    config: dict = {}


# LangSmith Studio expects these endpoints
@app.get("/assistants")
async def list_assistants():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.get("/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    return {"assistant_id": assistant_id, "graph_id": "agent", "config": {}}


@app.post("/assistants/{assistant_id}/runs/stream")
async def stream_run(
    assistant_id: str,
    request: RunRequest,
    x_api_key: str = Header(None, alias="X-Api-Key"),
):
    try:
        from agent import create_sql_deep_agent

        agent = create_sql_deep_agent()

        messages = request.input.get("messages", [])
        user_message = messages[-1]["content"] if messages else ""

        result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})

        final_message = result["messages"][-1]
        answer = (
            final_message.content
            if hasattr(final_message, "content")
            else str(final_message)
        )

        async def event_generator():
            yield f"data: {answer}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/runs/stream")
async def stream_run_root(
    request: RunRequest, x_api_key: str = Header(None, alias="X-Api-Key")
):
    return await stream_run("agent", request, x_api_key)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/info")
async def info():
    return {"version": "0.1.0", "name": "text2sql-agent", "runtime": "in-memory"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8024)
