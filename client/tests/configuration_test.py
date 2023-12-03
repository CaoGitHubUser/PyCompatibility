"""
Tests for configuration.py

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

import tempfile
import unittest
from pathlib import Path

from ..configuration import (
    CheckConfiguration,
    ReadConfigurationError,
    WriteConfigurationError,
)
from .test_logging import redirect_log_with_config


class TestWriteCheckConfiguration(unittest.TestCase):
    origin_configuration: CheckConfiguration = CheckConfiguration(
        False, 8, 10, "text", (), ()
    )

    def test_serialize(self) -> None:
        self.assertEqual(
            self.origin_configuration.serialize(),
            {
                "debug": False,
                "min_version": 8,
                "max_version": 10,
                "output": "text",
                "include": (),
                "exclude": (),
            },
        )

    def test_to_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            self.origin_configuration.to_file(tmp_root / "Compat.toml")
            self.assertEqual(
                (tmp_root / "Compat.toml").read_text(encoding="UTF-8"),
                "debug = false"
                + "\n"
                + "min_version = 8"
                + "\n"
                + "max_version = 10"
                + "\n"
                + 'output = "text"'
                + "\n"
                + "include = []"
                + "\n"
                + "exclude = []"
                + "\n",
            )

    def test_to_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            self.origin_configuration.to_file(tmp_root / "Compat.json")
            self.assertEqual(
                (tmp_root / "Compat.json").read_text(encoding="UTF-8"),
                "{"
                + "\n"
                + '    "debug": false,'
                + "\n"
                + '    "exclude": [],'
                + "\n"
                + '    "include": [],'
                + "\n"
                + '    "max_version": 10,'
                + "\n"
                + '    "min_version": 8,'
                + "\n"
                + '    "output": "text"'
                + "\n"
                + "}",
            )

    def test_to_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(tmp_root / "pyproject.toml", mode="w", encoding="UTF-8") as fp:
                fp.write("[tool.other_tools]" "\n" "other_cfg = []" "\n")
            self.origin_configuration.to_file(tmp_root / "pyproject.toml")
            self.assertEqual(
                (tmp_root / "pyproject.toml").read_text(encoding="UTF-8"),
                "[tool.other_tools]"
                + "\n"
                + "other_cfg = []"
                + "\n\n"
                + "[tool.PyCompatibility]"
                + "\n"
                + "debug = false"
                + "\n"
                + "min_version = 8"
                + "\n"
                + "max_version = 10"
                + "\n"
                + 'output = "text"'
                + "\n"
                + "include = []"
                + "\n"
                + "exclude = []"
                + "\n",
            )

    def test_write_to_invalid_file_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with self.assertRaises(WriteConfigurationError):
                self.origin_configuration.to_file(
                    tmp_root / "config.invalid_file_extension"
                )


class TestReadCheckConfiguration(unittest.TestCase):
    expected_result: CheckConfiguration = CheckConfiguration(
        True,
        8,
        10,
        "json",
        (Path("is_python_script/"),),
        (Path("not_python_script/"),),
    )

    def test_default(self) -> None:
        self.assertEqual(
            CheckConfiguration.from_dict({"min_version": "8", "max_version": "10"}),
            CheckConfiguration(False, 8, 10, "text", (), ()),
        )

    def test_from_dict(self) -> None:
        self.assertEqual(
            CheckConfiguration.from_dict(
                {
                    "min_version": 8,
                    "max_version": 10,
                    "include": ["is_python_script/"],
                    "exclude": ["not_python_script/"],
                    "output": "json",
                    "debug": True,
                }
            ),
            self.expected_result,
        )

    def test_from_version_list(self) -> None:
        self.assertEqual(
            CheckConfiguration.from_dict(
                {
                    "version": ["8", "10"],
                    "include": ["is_python_script/"],
                    "exclude": ["not_python_script/"],
                    "output": "json",
                    "debug": True,
                }
            ),
            self.expected_result,
        )

    def test_from_json(self) -> None:
        json_config: str = """\
        {
            "min_version": 8,
            "max_version": 10,
            "include": [
                "is_python_script/"
            ],
            "exclude": [
                "not_python_script/"
            ],
            "output": "json",
            "debug": true
        }
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)

            with open(tmp_root / "Compat.json", mode="w", encoding="UTF-8") as fp:
                fp.write(json_config)
            self.assertEqual(
                CheckConfiguration.from_file(tmp_root / "Compat.json"),
                self.expected_result,
            )

    def test_from_toml(self) -> None:
        toml_config: str = """\
        min_version = 8
        max_version = 10
        include = ["is_python_script/"]
        exclude = ["not_python_script/"]
        output = "json"
        debug = true
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(tmp_root / "Compat.toml", mode="w", encoding="UTF-8") as fp:
                fp.write(toml_config)
            self.assertEqual(
                CheckConfiguration.from_file(tmp_root / "Compat.toml"),
                self.expected_result,
            )

    def test_from_pyproject(self) -> None:
        pyproject_config: str = """\
        [tool.PyCompatibility]
        min_version = 8
        max_version = 10
        include = ["is_python_script/"]
        exclude = ["not_python_script/"]
        output = "json"
        debug = true
        """
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(tmp_root / "pyproject.toml", mode="w", encoding="UTF-8") as fp:
                fp.write(pyproject_config)
            self.assertEqual(
                CheckConfiguration.from_file(tmp_root / "pyproject.toml"),
                self.expected_result,
            )

    def test_invalid_configuration_file_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            Path.touch(tmp_root / "config.invalid_file_extension")
            with self.assertRaises(ReadConfigurationError):
                CheckConfiguration.from_file(tmp_root / "config.invalid_file_extension")

    def test_unused_configuration_warning(self) -> None:
        with redirect_log_with_config() as buf:
            CheckConfiguration.from_dict({"version": ["8", "10"], "unused": "unused"})
            self.assertEqual(
                buf.getvalue(),
                "[Warning] UnusedConfigurationWarning: Unused configuration: unused\n",
            )
