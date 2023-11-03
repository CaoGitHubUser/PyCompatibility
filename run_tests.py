"""
This is a script to run all the tests.
"""

import os
import re
import subprocess
from typing import List

import log

LOG: log.Logger = log.getLogger()
LOG.setLevel(log.DEBUG)
log.ensure_color_log()

# TODO: use annotation instead when Python 3.8 EOL
TEST_FILE = re.compile(r"(test_(.*).py)|((.*)_test.py)")  # type: re.Pattern[str]


def main() -> int:
    # Search test files

    test_files: List[str] = []
    LOG.debug("Searching for test files...")

    for path, _, files in os.walk("."):
        for file in files:
            if TEST_FILE.fullmatch(file) is not None:
                test_files.append(f"{path}/{file}")

    # TODO: use f"{'\n'.join(...)}" instead when Python 3.11 EOL
    LOG.info("Found these test files:\n" "{}".format("\n".join(test_files)))

    LOG.info("Running checks...")
    command: List[str] = ["python", "-m", "unittest", "--verbose"] + test_files
    exitcode: int = subprocess.run(command).returncode

    return exitcode


if __name__ == "__main__":
    exit(main())
