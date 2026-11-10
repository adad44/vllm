# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project

import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "tools/report_build_time_ninja.py"


@pytest.mark.parametrize(
    ("records", "expected"),
    [
        ("", "No build steps found."),
        ("0\t1\t0\tunfinished.o\n", "No build steps found."),
        (
            "0\t0\t0\tfast.o\t123\n",
            (
                "0.0 s weighted time (0.0 s elapsed time sum, 0.0x parallelism)\n"
                "    1 build steps completed, average of 0.00/s"
            ),
        ),
        (
            "0\t2000\t0\tfirst.o\t123\n1000\t3000\t0\tsecond.o\t456\n",
            (
                "3.0 s weighted time (4.0 s elapsed time sum, 1.3x parallelism)\n"
                "    2 build steps completed, average of 0.67/s"
            ),
        ),
    ],
    ids=["empty", "interrupted", "zero-duration", "parallel"],
)
def test_build_time_report(tmp_path: Path, records: str, expected: str):
    """Even an empty or sub-millisecond build must produce a usable report."""
    (tmp_path / ".ninja_log").write_text("# ninja log v5\n" + records)

    result = subprocess.run(
        [sys.executable, str(SCRIPT), "-C", str(tmp_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert expected in result.stdout
