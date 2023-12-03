"""
Tests for log.py

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

import contextlib
import io
import unittest
from typing import Any, Generator, Optional

from .. import log

from ..exception import static_assert


@contextlib.contextmanager
def redirect_log_with_config(
    basic: bool = False, color: bool = False, **kwargs: Any
) -> Generator[io.StringIO, None, None]:
    buf: Optional[io.StringIO] = kwargs.pop("stream", None)
    if buf is None:
        buf = io.StringIO()
    kwargs["stream"] = buf
    static_assert(not color or not basic, ValueError("color and basic were both True!"))
    kwargs["force"] = True
    if color:
        log.config_with_colored_handler(**kwargs)
    elif not basic:
        log.config_with_formatted_handler(**kwargs)
    else:
        log.basicConfig(**kwargs)

    try:
        yield buf
    finally:
        buf.close()


class CheckFormattedStreamHandler(unittest.TestCase):
    def test_debug(self) -> None:
        with redirect_log_with_config(level=log.DEBUG) as buf:
            log.debug("A debug message")
            self.assertEqual(buf.getvalue(), "[Debug] A debug message\n")

    def test_info(self) -> None:
        with redirect_log_with_config(level=log.INFO) as buf:
            log.info("An info message")
            self.assertEqual(buf.getvalue(), "[Info] An info message\n")

    def test_warning(self) -> None:
        with redirect_log_with_config() as buf:
            log.warning("A warning message")
            self.assertEqual(buf.getvalue(), "[Warning] A warning message\n")

    def test_error(self) -> None:
        with redirect_log_with_config() as buf:
            log.error("An error message")
            self.assertEqual(buf.getvalue(), "[Error] An error message\n")

    def test_critical(self) -> None:
        with redirect_log_with_config() as buf:
            log.critical("An critical error message")
            self.assertEqual(buf.getvalue(), "Fatal error: An critical error message\n")

    def test_no_level(self) -> None:
        with redirect_log_with_config() as buf:
            log.log(35, "This will logged as is")
            self.assertEqual(buf.getvalue(), "This will logged as is\n")
