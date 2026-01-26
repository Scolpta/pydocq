"""Extract usage examples from test files.

This module provides functionality to extract real usage examples
from test files using grep-based pattern matching.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class UsageExample:
    """Extracted usage example."""

    code: str
    source_file: str
    line_number: int
    context: str


def extract_examples_from_tests(
    function_name: str, test_dirs: List[str] = None, max_examples: int = 10
) -> List[UsageExample]:
    """Extract usage examples from test files using grep-like approach.

    Args:
        function_name: Name of function to find examples for
        test_dirs: List of test directory paths
        max_examples: Maximum number of examples to extract

    Returns:
        List of usage examples
    """
    if test_dirs is None:
        test_dirs = ["tests/", "test/", "tests/"]

    examples = []

    # Search pattern: function_name(
    # Match: function_name(...), capturing context
    pattern = rf"([^\n]*{re.escape(function_name)}\s*\([^)]*\)[^\n]*)"

    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if not test_path.exists():
            continue

        # Find all Python files
        for py_file in test_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split("\n")

                # Search for pattern
                for i, line in enumerate(lines):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        code_snippet = match.group(1).strip()

                        # Filter out non-call lines
                        if not _is_valid_call(code_snippet, function_name):
                            continue

                        # Get context (previous line + current line)
                        context = _get_context(lines, i)

                        examples.append(
                            UsageExample(
                                code=code_snippet,
                                source_file=str(py_file),
                                line_number=i + 1,
                                context=context,
                            )
                        )

                        # Limit examples per function
                        if len(examples) >= max_examples:
                            return examples

            except Exception:
                # Skip files that can't be read
                continue

    return examples


def extract_examples_from_tests_for_target(
    target_path: str, test_dirs: List[str] = None, max_examples: int = 10
) -> List[UsageExample]:
    """Extract usage examples for a specific target path.

    Args:
        target_path: Full target path (e.g., "json.dump" or "pandas.DataFrame.merge")
        test_dirs: List of test directory paths
        max_examples: Maximum number of examples to extract

    Returns:
        List of usage examples
    """
    # Extract the function/method name from the path
    # For "json.dump", we search for "dump("
    # For "pandas.DataFrame.merge", we search for ".merge(" or "DataFrame(...).merge("
    parts = target_path.split(".")
    function_name = parts[-1]

    # For module.function or class.method, also search with context
    if len(parts) >= 2:
        # Create patterns that match both "function(" and "obj.function("
        return extract_examples_from_tests(function_name, test_dirs, max_examples)

    return extract_examples_from_tests(function_name, test_dirs, max_examples)


def _is_valid_call(code: str, function_name: str) -> bool:
    """Check if code is a valid function call.

    Args:
        code: Code snippet to check
        function_name: Function name to match

    Returns:
        True if valid call
    """
    # Must have opening parenthesis
    if "(" not in code:
        return False

    # Skip definitions
    if code.strip().startswith("def "):
        return False

    # Skip imports
    if "import " in code or "from " in code:
        return False

    # Skip comments
    if code.strip().startswith("#"):
        return False

    # Skip async definitions
    if code.strip().startswith("async def "):
        return False

    # Skip class definitions
    if code.strip().startswith("class "):
        return False

    return True


def _get_context(lines: List[str], line_idx: int) -> str:
    """Get context around a line.

    Args:
        lines: All lines in file
        line_idx: Index of current line

    Returns:
        Context string (previous 2 lines + current line + next 2 lines)
    """
    start = max(0, line_idx - 2)
    end = min(len(lines), line_idx + 3)
    context_lines = lines[start:end]

    # Add line numbers
    context = "\n".join(f"{i + start + 1}: {line}" for i, line in enumerate(context_lines))

    return context
