"""Pin the format the architecture.md renderer expects to find.

The renderer walks ``docs/architecture.md`` looking for six concrete
number-bearing claims and replaces the digit with the live inventory.  A
doc that doesn't match (typo, restructure, removed table) raises on the
first non-matching claim rather than silently leaving stale numbers.
These tests pin the location and shape of those claims.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from tools.package_inventory import inventory, source_locks

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "architecture.md"
RENDERER = ROOT / "tools" / "render_architecture_counts.py"


def _expected_counts() -> dict[str, int]:
    records = inventory(ROOT)
    locks = source_locks(ROOT)
    return {
        "n_recipes": len(records),
        "n_packit": sum(record.packit_configured for record in records),
        "n_locks": len(locks),
        "n_staged": sum("stage" in lock for lock in locks.values()),
    }


def _number_after_line(text: str, prefix: str) -> str:
    """Return the digit-block on the line that begins with ``prefix``."""
    for line in text.splitlines():
        if line.startswith(prefix):
            match = re.search(r"\b(\d+)\b", line)
            assert match, f"no digit in line {line!r}"
            return match.group(1)
    raise AssertionError(f"no line begins with {prefix!r} in architecture.md")


def test_architecture_doc_has_every_claim_the_renderer_replaces() -> None:
    text = DOC.read_text(encoding="utf-8")
    expected = _expected_counts()
    n = expected["n_recipes"]

    assert _number_after_line(text, "| `ls -d packages/*/") == str(n)
    assert _number_after_line(text, "| entries under `.packit.yaml:packages`") == str(
        expected["n_packit"]
    )
    assert _number_after_line(
        text, "| entries under `config/upstream-sources.json:packages`"
    ) == str(expected["n_locks"])
    # 'cover all N recipes' and 'a list of N satisfies' both target the recipe
    # count; either clause rewriting would break the renderer.
    cover = re.search(r"cover all (\d+) recipes", text)
    assert cover and cover.group(1) == str(n)
    satisfies = re.search(r"a list of (\d+) satisfies", text)
    assert satisfies and satisfies.group(1) == str(n)
    validated = re.search(r"validated (\d+) source RPMs", text)
    assert validated and validated.group(1) == str(n)
    staged = re.search(
        r"^(\d+) of \d+ packages carry a hand-assigned `stage`",
        text,
        flags=re.MULTILINE,
    )
    assert staged and staged.group(1) == str(expected["n_staged"])


def test_renderer_is_a_noop_when_doc_is_current() -> None:
    """The workflow runs the renderer, then `pytest tests -q`.  If the
    renderer were a no-op only because the doc already matches, a missed
    rebuild would not move the doc forward — the renderer must accept a
    already-current doc and exit 0.
    """
    result = subprocess.run(
        [sys.executable, str(RENDERER)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"renderer exited {result.returncode} on a current doc:\n"
        f"{result.stdout}{result.stderr}"
    )


def test_renderer_rewrites_every_claim_to_match_the_inventory() -> None:
    """Round-trip: rewrite with --write, then re-read the doc and assert
    every claim matches.  Tests the regex patterns, not just the
    inventory; if a pattern silently stops matching, this test catches it.
    """
    result = subprocess.run(
        [sys.executable, str(RENDERER), "--write"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    text = DOC.read_text(encoding="utf-8")
    expected = _expected_counts()
    n = expected["n_recipes"]
    assert _number_after_line(text, "| `ls -d packages/*/") == str(n)
    assert _number_after_line(text, "| entries under `.packit.yaml:packages`") == str(
        expected["n_packit"]
    )
    assert _number_after_line(
        text, "| entries under `config/upstream-sources.json:packages`"
    ) == str(expected["n_locks"])
    cover = re.search(r"cover all (\d+) recipes", text)
    assert cover and cover.group(1) == str(n)
    satisfies = re.search(r"a list of (\d+) satisfies", text)
    assert satisfies and satisfies.group(1) == str(n)
    validated = re.search(r"validated (\d+) source RPMs", text)
    assert validated and validated.group(1) == str(n)
    staged = re.search(
        r"^(\d+) of \d+ packages carry a hand-assigned `stage`",
        text,
        flags=re.MULTILINE,
    )
    assert staged and staged.group(1) == str(expected["n_staged"])