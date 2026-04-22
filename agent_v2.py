import argparse
import json
import os
import sys
import time
import argparse
from typing import Any

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()

console = Console()

DEFAULT_BENCHMARK_QUERIES = [
    "How many customers are from Canada?",
    "What are the top 5 best-selling artists?",
    "Which employee generated the most revenue?",
    "List all albums by artists from the USA",
    "How many invoices were created in 2023?",
]


def create_sql_deep_agent():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "chinook.db")
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}", sample_rows_in_table_info=3)
    model = ChatNVIDIA(model="deepseek-ai/deepseek-v3.1-terminus", temperature=0)

    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    sql_tools = toolkit.get_tools()

    agent = create_deep_agent(
        model=model,
        memory=["./AGENTS.md"],
        skills=["./skills/"],
        tools=sql_tools,
        subagents=[],
        backend=FilesystemBackend(root_dir=base_dir),
    )
    return agent


def run_with_debug(question: str, debug: bool = False) -> dict[str, Any]:
    start_time = time.perf_counter()
    tool_calls = []
    tokens_used = {"input": 0, "output": 0, "total": 0}

    if debug:
        console.print("[dim]Creating SQL Deep Agent...[/dim]")

    agent = create_sql_deep_agent()

    if debug:
        console.print("[dim]Processing query with debug...[/dim]\n")

    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    elapsed_time = time.perf_counter() - start_time

    for msg in result.get("messages", []):
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    {
                        "tool": tc.get("name", "unknown"),
                        "args": tc.get("args", {}),
                    }
                )

        if hasattr(msg, "usage_metadata") and msg.usage_metadata:
            usage = msg.usage_metadata
            tokens_used = {
                "input": usage.get("input_tokens", 0),
                "output": usage.get("output_tokens", 0),
                "total": usage.get("total_tokens", 0),
            }

    final_message = result["messages"][-1]
    answer = (
        final_message.content
        if hasattr(final_message, "content")
        else str(final_message)
    )

    if debug:
        console.print(f"\n[bold yellow]=== DEBUG ===[/bold yellow]")
        console.print(f"[dim]Total time: {elapsed_time:.2f}s[/dim]")
        if tool_calls:
            console.print(f"[dim]Tool calls: {len(tool_calls)}[/dim]")
        console.print()

    return {
        "answer": answer,
        "elapsed_time": elapsed_time,
        "tool_calls": tool_calls,
        "tokens": tokens_used,
    }


def run_benchmark(queries=None, output_file=None):
    questions = queries if queries else DEFAULT_BENCHMARK_QUERIES

    console.print(
        Panel("[bold cyan]Running Benchmark[/bold cyan]", border_style="cyan")
    )
    console.print(f"[dim]Running {len(questions)} queries...[/dim]\n")

    results = []
    total_tokens = {"input": 0, "output": 0, "total": 0}
    total_time = 0.0
    success_count = 0

    for i, question in enumerate(questions, 1):
        console.print(f"[dim]({i}/{len(questions)}) {question[:50]}...[/dim]")
        try:
            result = run_with_debug(question, debug=False)
            success = True
            error_msg = None
            success_count += 1
            for key in ("input", "output", "total"):
                total_tokens[key] += result["tokens"][key]
            total_time += result["elapsed_time"]
        except Exception as e:
            success = False
            error_msg = str(e)
            result = {
                "answer": None,
                "elapsed_time": 0,
                "tokens": {"input": 0, "output": 0, "total": 0},
            }

        results.append(
            {
                "question": question,
                "success": success,
                "error": error_msg,
                "elapsed_time": result.get("elapsed_time", 0),
                "tokens": result.get("tokens", {"input": 0, "output": 0, "total": 0}),
            }
        )

    summary = {
        "total_queries": len(questions),
        "success_count": success_count,
        "success_rate": round(100 * success_count / len(questions), 1)
        if questions
        else 0,
        "total_time": round(total_time, 2),
        "avg_time": round(total_time / len(questions), 2) if questions else 0,
        "total_tokens": total_tokens,
    }

    table = Table(title="Benchmark Results")
    table.add_column("#", style="dim", width=3)
    table.add_column("Question", style="cyan", max_width=40)
    table.add_column("Time", justify="right", style="dim")
    table.add_column("Tokens", justify="right", style="dim")
    table.add_column("Status", justify="center")

    for i, r in enumerate(results, 1):
        status = "[green]OK[/green]" if r["success"] else "[red]FAIL[/red]"
        table.add_row(
            str(i),
            r["question"][:40] + "...",
            f"{r['elapsed_time']:.2f}s",
            str(r["tokens"]["total"]),
            status,
        )

    console.print()
    console.print(table)
    console.print()

    summary_table = Table(title="Summary", box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    summary_table.add_row("Total", str(summary["total_queries"]))
    summary_table.add_row("Success", f"{summary['success_rate']}%")
    summary_table.add_row("Time", f"{summary['total_time']}s")
    summary_table.add_row("Tokens", str(summary["total_tokens"]["total"]))
    console.print(summary_table)

    report = {
        "version": "1.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": results,
        "summary": summary,
    }

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        console.print(f"\n[dim]Saved to {output_file}[/dim]")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Text-to-SQL Deep Agent v2 (OpenRouter)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("question", type=str, nargs="?", help="Question to ask")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    parser.add_argument("--benchmark-queries", type=str, help="JSON file with queries")
    parser.add_argument("--benchmark-output", type=str, help="Output JSON file")

    args = parser.parse_args()

    if args.benchmark:
        queries = None
        if args.benchmark_queries:
            with open(args.benchmark_queries) as f:
                data = json.load(f)
                queries = [q["question"] for q in data.get("queries", [])]
        run_benchmark(queries=queries, output_file=args.benchmark_output)
        return

    if not args.question:
        parser.print_help()
        sys.exit(1)

    console.print(
        Panel(f"[bold cyan]Question:[/bold cyan] {args.question}", border_style="cyan")
    )
    console.print()

    try:
        result = run_with_debug(args.question, debug=args.debug)
        answer = result["answer"]
        console.print(
            Panel(f"[bold green]Answer:[/bold green]\n\n{answer}", border_style="green")
        )
    except Exception as e:
        console.print(
            Panel(f"[bold red]Error:[/bold red]\n\n{str(e)}", border_style="red")
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
