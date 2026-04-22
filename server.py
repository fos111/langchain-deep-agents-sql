import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
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


class RunRequest(BaseModel):
    assistant_id: str = "agent"
    input: dict
    stream_mode: str = "updates"


class AssistantConfig(BaseModel):
    assistant_id: str
    config: dict = {}


@app.get("/assistants")
async def list_assistants():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.post("/assistants")
async def create_assistant():
    return {"assistant_id": "agent", "graph_id": "agent"}


@app.get("/assistants/search")
async def search_assistants():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.post("/assistants/search")
async def search_assistants_post():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.get("/assistants/info")
async def assistants_info():
    return {"assistants": [{"assistant_id": "agent", "graph_id": "agent"}]}


@app.get("/assistant/info")
async def assistant_info():
    return {"assistant_id": "agent", "graph_id": "agent"}


@app.get("/threads")
async def list_threads():
    return []


@app.post("/assistants")
async def create_assistant():
    return {"assistant_id": "agent", "graph_id": "agent"}


@app.get("/assistants/search")
async def search_assistants():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.post("/assistants/search")
async def search_assistants_post():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.post("/assistants")
async def create_assistant():
    return {"assistant_id": "agent", "graph_id": "agent"}


@app.get("/assistants/search")
async def search_assistants():
    return ["agent"]


@app.post("/assistants/search")
async def search_assistants_post():
    return ["agent"]


@app.post("/assistants")
async def create_assistant():
    return {"assistant_id": "agent", "graph_id": "agent"}


@app.get("/assistants/search")
async def search_assistants():
    return []


@app.post("/assistants/search")
async def search_assistants_post():
    return []


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
        import json
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
            run_id = "run_" + str(hash(user_message))[:8]
            yield f"event: run_created\ndata: {json.dumps({{'run_id': run_id}})}\n\n"
            yield f"event: metadata\ndata: {json.dumps({{'run_id': run_id, 'assistant_id': assistant_id}})}\n\n"
            yield f"data: {json.dumps({{'messages': [{{'role': 'assistant', 'content': answer}}]}})}\n\n"
            yield f"event: done\ndata: {json.dumps({{'run_id': run_id}})}\n\n"

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


@app.get("/")
async def root():
    return {"status": "ok", "message": "Text-to-SQL Agent API"}


@app.post("/assistants/search")
async def search_assistants():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.get("/assistants/search")
async def search_assistants_get():
    return [{"assistant_id": "agent", "graph_id": "agent", "config": {}}]


@app.get("/assistants/info")
async def assistants_info():
    return {"assistants": [{"assistant_id": "agent", "graph_id": "agent"}]}


@app.get("/assistant/info")
async def assistant_info():
    return {"assistant_id": "agent", "graph_id": "agent"}


@app.get("/assistants/{assistant_id}/schemas")
async def get_assistant_schema(assistant_id: str):
    return {"input_schema": {}, "config_schema": {}, "output_schema": {}}


@app.get("/assistants/{assistant_id}/subgraphs")
async def get_subgraphs(assistant_id: str, recurse: bool = False):
    return {"subgraphs": {}}


@app.get("/assistants/{assistant_id}/graph")
async def get_graph(assistant_id: str, xray: bool = False):
    mermaid = """graph TD;
        User([User])-->Agent;
        Agent-->Tools;
        Tools-->Agent;
        Agent-->Output([Output]);
    """
    return {"draw": mermaid, "mermaid": mermaid, "version": "0.1.0"}


@app.get("/assistants/{assistant_id}/versions")
async def get_versions(assistant_id: str):
    return {"version": "0.1.0", "agent": "text2sql-agent"}


@app.post("/store/namespaces")
async def create_namespace():
    return {"namespace": "default"}


@app.get("/store/namespaces")
async def list_namespaces():
    return [{"name": "default"}]


@app.get("/store/namespaces/{namespace}/objects")
async def list_objects(namespace: str):
    return {"objects": [], "has_more": False}


@app.post("/threads")
async def create_thread():
    import uuid

    thread_id = str(uuid.uuid4())
    return {"thread_id": thread_id, "created_at": "", "metadata": {}}


@app.get("/threads")
async def list_threads():
    return []


@app.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    return {"thread_id": thread_id, "created_at": "", "metadata": {}}


@app.delete("/threads/{thread_id}")
async def delete_thread(thread_id: str):
    return {"deleted": True}


@app.get("/threads/{thread_id}/history")
async def get_thread_history(thread_id: str):
    return []


@app.get("/threads/{thread_id}/runs")
async def list_thread_runs(
    thread_id: str, limit: int = 1000, offset: int = 0, status: str = None
):
    return {"runs": [], "has_more": False}


@app.post("/threads/{thread_id}/runs/stream")
async def stream_thread_run(
    thread_id: str,
    request: RunRequest,
    x_api_key: str = Header(None, alias="X-Api-Key"),
):
    try:
        import json
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
            run_id = "run_" + str(hash(user_message))[:8]
            yield f"event: run_created\ndata: {json.dumps({{'run_id': run_id}})}\n\n"
            yield f"event: metadata\ndata: {json.dumps({{'run_id': run_id, 'assistant_id': 'agent'}})}\n\n"
            yield f"data: {json.dumps({{'messages': [{{'role': 'assistant', 'content': answer}}]}})}\n\n"
            yield f"event: done\ndata: {json.dumps({{'run_id': run_id}})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/threads/{thread_id}/history")
async def update_thread_history(thread_id: str):
    return {"updated": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8024)
