"""
Goal Agent Utilities

Helper functions for the Goal Setting and Monitoring pattern.
"""

import re


def clean_code_block(code: str) -> str:
    """Remove markdown code fences from generated code."""
    lines = code.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def add_comment_header(code: str, use_case: str) -> str:
    """Add a comment header describing the use case."""
    comment = f"# This Python program implements the following use case:\n# {use_case.strip()}\n"
    return comment + "\n" + code


def to_snake_case(text: str) -> str:
    """Convert text to snake_case for filenames."""
    text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    return re.sub(r"\s+", "_", text.strip().lower())
