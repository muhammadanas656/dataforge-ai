import re
from src.llm import tracked_chat

DRAFT_PROMPT = """You are a senior plugin author for DataForge AI.
Write a clean, modular Python plugin that subclasses either BaseSource or BaseAnalysis from src.plugins and follows the contract exactly.
Use only safe standard libraries (pandas, numpy, math, re).
NEVER use eval, exec, subprocess, os.system, socket, or network access.
Return ONLY valid Python code without markdown code fences, headers, or conversational commentary."""

def draft(run_id, request):
    text = tracked_chat(
        run_id, "PLUGIN", "drafter",
        [
            {"role": "system", "content": DRAFT_PROMPT},
            {"role": "user", "content": request}
        ],
        temperature=0.2,
        max_completion_tokens=800
    )
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return text
