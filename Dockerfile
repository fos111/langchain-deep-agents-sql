FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv pip install -e .

COPY . .

EXPOSE 8024

CMD ["langgraph", "up", "--port", "8024"]