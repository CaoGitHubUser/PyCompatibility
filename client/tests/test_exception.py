"""
Tests for exception.py

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

import unittest

from ..exception import static_assert, warn
from .test_logging import redirect_log_with_config


class TestStaticAssert(unittest.TestCase):
    def test_raise(self) -> None:
        with self.assertRaises(RuntimeError):
            static_assert(False, RuntimeError)

    def test_exc_is_instance(self) -> None:
        try:
            static_assert(False, RuntimeError("Runtime error!"))
        except RuntimeError as exc:
            self.assertEqual(str(exc), "Runtime error!")

    def test_both_exc_instance_msg(self) -> None:
        with self.assertRaises(ValueError):
            static_assert(True, RuntimeError("Runtime error!"), "Runtime error!")
        with self.assertRaises(ValueError):
            static_assert(False, RuntimeError("Runtime error!"), "Runtime error!")

    def test_warn(self) -> None:
        with redirect_log_with_config() as buf:
            warn("A warning", UserWarning)
            self.assertEqual(buf.getvalue(), "[Warning] UserWarning: A warning\n")

    def test_warn_msg_is_waring_instance(self) -> None:
        with redirect_log_with_config() as buf:
            warn(UserWarning("Another warning"))
            self.assertEqual(buf.getvalue(), "[Warning] UserWarning: Another warning\n")
