import os
from dotenv import load_dotenv
from langgraph_api.server import app

load_dotenv()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8024)
