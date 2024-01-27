"""
Tests for log.py

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

import contextlib
import io
import logging
import unittest
from typing import Any, Generator, Optional

from .. import log

from ..exception import assert_exc

LOG: logging.Logger = logging.getLogger("test_logging")


@contextlib.contextmanager
def redirect_log_with_config(
    basic: bool = False, color: bool = False, **kwargs: Any
) -> Generator[io.StringIO, None, None]:
    buf: Optional[io.StringIO] = kwargs.pop("stream", None)
    if buf is None:
        buf = io.StringIO()
    kwargs["stream"] = buf
    assert_exc(
        not color or not basic, ValueError("color and basic were both True!")
    )
    kwargs["force"] = True
    if color:
        log.config_with_colored_handler(**kwargs)
    elif not basic:
        log.config_with_formatted_handler(**kwargs)
    else:
        logging.basicConfig(**kwargs)

    try:
        yield buf
    finally:
        buf.close()


class CheckFormattedStreamHandler(unittest.TestCase):
    def test_debug(self) -> None:
        with redirect_log_with_config(level=logging.DEBUG) as buf:
            LOG.debug("A debug message")
            self.assertEqual(
                buf.getvalue(), "[Debug] test_logging: A debug message\n"
            )

    def test_info(self) -> None:
        with redirect_log_with_config(level=logging.INFO) as buf:
            LOG.info("An info message")
            self.assertEqual(
                buf.getvalue(), "[Info] test_logging: An info message\n"
            )

    def test_warning(self) -> None:
        with redirect_log_with_config() as buf:
            LOG.warning("A warning message")
            self.assertEqual(
                buf.getvalue(), "[Warning] test_logging: A warning message\n"
            )

    def test_error(self) -> None:
        with redirect_log_with_config() as buf:
            LOG.error("An error message")
            self.assertEqual(
                buf.getvalue(), "[Error] test_logging: An error message\n"
            )

    def test_critical(self) -> None:
        with redirect_log_with_config() as buf:
            LOG.critical("An critical error message")
            self.assertEqual(
                buf.getvalue(),
                "Fatal error: test_logging: An critical error message\n",
            )

    def test_no_level(self) -> None:
        with redirect_log_with_config() as buf:
            LOG.log(35, "This will logged as is")
            self.assertEqual(
                buf.getvalue(), "test_logging: This will logged as is\n"
            )

    def test_initialize(self) -> None:
        for h in logging.root.handlers:
            logging.root.removeHandler(h)
            h.close()
        buf = io.StringIO()
        log.initialize("DEBUG", False, buf)

        log.initialize("ERROR", True)
        self.assertEqual(
            buf.getvalue(), "[Debug] log: Already initialized, skipping.\n"
        )

        log.success("A record with level SUCCESS", logger=LOG)
        self.assertEqual(
            buf.getvalue(),
            "[Debug] log: Already initialized, skipping.\n"
            "[Success] test_logging: A record with level SUCCESS\n",
        )

        for h in logging.root.handlers:
            logging.root.removeHandler(h)
            h.close()
        buf.close()
        logging.basicConfig(level="INFO")
