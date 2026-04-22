"""Unit tests for TraceCallbackHandler."""

import pytest
from agent import TraceCallbackHandler
from langchain_core.outputs import LLMResult


class TestTraceCallbackHandler:
    def test_init(self):
        handler = TraceCallbackHandler()
        assert handler.trace_events == []
        assert handler._current_llm is None

    def test_on_llm_start_end(self):
        handler = TraceCallbackHandler()
        handler.on_llm_start({}, ["prompt"])
        assert handler._current_llm is not None
        handler.on_llm_end(LLMResult(generations=[]))
        assert len(handler.trace_events) == 1
        assert handler.trace_events[0]["name"] == "LLM"
        assert handler.trace_events[0]["duration"] >= 0

    def test_on_tool_start_end(self):
        handler = TraceCallbackHandler()
        handler.on_tool_start({"name": "list_tables"}, None)
        handler.on_tool_end("tables output")
        assert len(handler.trace_events) == 1
        assert handler.trace_events[0]["name"] == "list_tables"

    def test_multiple_events(self):
        handler = TraceCallbackHandler()
        handler.on_llm_start({}, ["prompt"])
        handler.on_llm_end(LLMResult(generations=[]))
        handler.on_tool_start({"name": "execute_query"}, "SELECT 1")
        handler.on_tool_end("result")
        handler.on_tool_start({"name": "get_schema"}, "customers")
        handler.on_tool_end("schema")

        assert len(handler.trace_events) == 3
        assert handler.trace_events[0]["step"] == 1
        assert handler.trace_events[1]["step"] == 2
        assert handler.trace_events[2]["step"] == 3
