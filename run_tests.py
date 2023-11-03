"""
This is a script to run all the tests.
"""

import logging
import os
import re
import subprocess
from typing import List

import log

LOG: logging.Logger = logging.getLogger()
LOG.setLevel(logging.DEBUG)
log.ensure_color_log()

TEST_FILE: re.Pattern[str] = re.compile(r"(test_(.*).py)|((.*)_test.py)")


def main() -> int:
    # Search test files

    test_files: List[str] = []
    LOG.debug("Searching for test files...")

    for path, _, files in os.walk("."):
        for file in files:
            if TEST_FILE.fullmatch(file) is not None:
                test_files.append(f"{path}/{file}")

    LOG.info("Found these test files:\n" "{}".format("\n".join(test_files)))

    LOG.info("Running checks...")
    command: List[str] = ["python", "-m", "unittest"] + test_files
    exitcode: int = subprocess.run(command).returncode

    return exitcode


if __name__ == "__main__":
    exit(main())
