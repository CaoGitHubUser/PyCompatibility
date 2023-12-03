"""
A script to run all tests.

Copyright (C) 2023  Cao Bo Wen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import os
import re
import shlex
import subprocess
from typing import List, Pattern

from client import log

TEST_FILE: Pattern[str] = re.compile(r"(test_(.*).py)|((.*)_test.py)")
LOG: log.Logger = log.getLogger(__file__)
log.config_with_colored_handler()
unix_cwd: str = os.getcwd().replace("\\", "/")
current_dir_name: str = os.path.split(unix_cwd)[1]


def main(cov: bool) -> int:
    # Search test files
    test_files: List[str] = []

    for path, _, files in os.walk("."):
        for file in files:
            if TEST_FILE.fullmatch(file) is not None:
                test_files.append(f"{path}/{file}".replace("\\", "/").replace("./", ""))
    # TODO: Use `f"{'\n'.format(...)}"` instead after EOL: Python 3.11
    LOG.debug("Found these test files:\n{}".format("\n".join(test_files)))

    test_files_in_parent_dir: List[str] = [
        f"{current_dir_name}/{test_file}" for test_file in test_files
    ]
    if cov:
        command = [
            "coverage",
            "run",
            "--source",
            current_dir_name,
            "--data-file",
            f"{current_dir_name}/.coverage",
            "--rcfile",
            f"{current_dir_name}/.coveragerc",
            "-m",
            "unittest",
            *test_files_in_parent_dir,
            "--verbose",
        ]
    else:
        command = ["python", "-m", "unittest", *test_files_in_parent_dir, "--verbose"]
    LOG.debug(
        f"Using command(in cwd {os.path.split(unix_cwd)[0]}):\n{shlex.join(command)}"
    )

    exitcode = subprocess.run(command, cwd="../").returncode
    return exitcode


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cov", action="store_true", default=False, help="Generate coverage report"
    )
    ap.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Print verbose debug messages",
    )
    args = ap.parse_args()

    if args.verbose:
        LOG.setLevel(log.DEBUG)
    exit(main(args.cov))
