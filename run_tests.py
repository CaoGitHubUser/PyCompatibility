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
import unittest
from typing import List, Pattern

import click

TEST_FILE: Pattern[str] = re.compile(r"(test_(.*).py)|((.*)_test.py)")
LOG: logging.Logger = logging.getLogger("tests_runner")
UNIX_CWD: str = os.getcwd().replace("\\", "/")
CURRENT_DIR_NAME: str = os.path.basename(UNIX_CWD)


@click.command
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Print verbose debug messages",
)
def main(verbose: bool) -> None:
    logging.basicConfig(level="DEBUG" if verbose else "INFO")

    # Search test files
    test_files: List[str] = []
    for path, _, files in os.walk("src/PyCompatibility"):
        for file in files:
            this_file: str = os.path.normpath(f"{path}/{file}").replace(
                "\\", "/"
            )
            if TEST_FILE.fullmatch(file) is not None:
                test_files.append(this_file)
    # TODO: Use `f"{'\n'.format(...)}"` instead after EOL: Python 3.11

    LOG.debug("Found these test files:\n{}".format("\n".join(test_files)))

    unittest.main(
        module=None, argv=[__file__, *test_files], verbosity=2, tb_locals=True
    )


if __name__ == "__main__":
    main()
