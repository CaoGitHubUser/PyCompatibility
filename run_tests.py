"""
A script to run all tests.

Copyright (C) 2023-2024  Bo Wen Cao

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

import logging
import os
import re
import shlex
import subprocess
import sys
from typing import List, Pattern

import click

from client import log

TEST_FILE: Pattern[str] = re.compile(r"(test_(.*).py)|((.*)_test.py)")
LOG: logging.Logger = logging.getLogger("tests_runner")
UNIX_CWD: str = os.getcwd().replace("\\", "/")
CURRENT_DIR_NAME: str = os.path.split(UNIX_CWD)[1]


@click.command
@click.option(
    "--cov", is_flag=True, default=False, help="Generate coverage report"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Print verbose debug messages",
)
@click.option("--color/--no-color", default=True, help="Colorful output")
def main(cov: bool, verbose: bool, color: bool) -> int:
    log.initialize("DEBUG" if verbose else "INFO", color)
    # Search test files
    test_files: List[str] = []

    for path, _, files in os.walk("."):
        for file in files:
            if TEST_FILE.fullmatch(file) is not None:
                test_files.append(
                    f"{path}/{file}".replace("\\", "/").replace("./", "")
                )
    # TODO: Use `f"{'\n'.format(...)}"` instead after EOL: Python 3.11
    LOG.debug("Found these test files:\n{}".format("\n".join(test_files)))

    test_files_in_parent_dir: List[str] = [
        f"{CURRENT_DIR_NAME}/{test_file}" for test_file in test_files
    ]
    if cov:
        command = [
            "coverage",
            "run",
            "--source",
            CURRENT_DIR_NAME,
            "--data-file",
            f"{CURRENT_DIR_NAME}/.coverage",
            "--rcfile",
            f"{CURRENT_DIR_NAME}/.coveragerc",
            "-m",
            "unittest",
            *test_files_in_parent_dir,
            "--verbose",
        ]
    else:
        command = [
            "python",
            "-m",
            "unittest",
            *test_files_in_parent_dir,
            "--verbose",
        ]
    LOG.debug(
        f"Using command(in cwd {os.path.split(UNIX_CWD)[0]}):\n"
        f"{shlex.join(command)}"
    )

    exitcode = subprocess.run(command, cwd="../").returncode
    return exitcode


if __name__ == "__main__":
    sys.exit(main())
