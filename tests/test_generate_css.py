"""
Smoke test for scripts/generate_css.py -- confirms it runs cleanly and
produces non-empty, well-formed CSS. Run via subprocess (rather than
importing scripts.generate_css directly) since scripts/ is deliberately
not part of the installed package -- see DESIGN.md section 8.
"""

import pathlib
import subprocess
import sys


def test_generate_css_runs_and_produces_selectors():
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    script = repo_root / "scripts" / "generate_css.py"

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )

    output = result.stdout
    assert "data-text=" in output
    assert "font-weight" in output
    # A handful of specific closed-class forms we know rules.py seeds.
    for form in ('"mu"', '"va"', '"cha"', '"no"'):
        assert form in output, f"expected {form} in generated CSS, got:\n{output}"


if __name__ == "__main__":
    test_generate_css_runs_and_produces_selectors()
    print("PASS test_generate_css_runs_and_produces_selectors")
