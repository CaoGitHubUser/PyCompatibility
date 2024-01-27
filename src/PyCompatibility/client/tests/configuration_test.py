"""
Tests for configuration.py

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

import tempfile
import unittest
from pathlib import Path

from ..configuration import (
    CheckConfiguration,
    ParseConfigurationError,
    ReadConfigurationError,
    WriteConfigurationError,
)
from .test_logging import redirect_log_with_config


class TestWriteCheckConfiguration(unittest.TestCase):
    origin_configuration: CheckConfiguration = CheckConfiguration(
        8, 10, Path("report.json"), set(), set()
    )

    def test_serialize(self) -> None:
        self.assertEqual(
            self.origin_configuration.serialize(),
            {
                "min_version": 8,
                "max_version": 10,
                "report": Path("report.json"),
                "include": set(),
                "exclude": set(),
            },
        )

    def test_to_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            self.origin_configuration.to_file(tmp_root / "Compat.toml")
            self.assertEqual(
                (tmp_root / "Compat.toml").read_text(encoding="UTF-8"),
                "min_version = 8"
                + "\n"
                + "max_version = 10"
                + "\n"
                + 'report = "report.json"'
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
                + '    "exclude": [],'
                + "\n"
                + '    "include": [],'
                + "\n"
                + '    "max_version": 10,'
                + "\n"
                + '    "min_version": 8,'
                + "\n"
                + '    "report": "report.json"'
                + "\n"
                + "}",
            )

    def test_to_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(
                tmp_root / "pyproject.toml", mode="w", encoding="UTF-8"
            ) as fp:
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
                + "min_version = 8"
                + "\n"
                + "max_version = 10"
                + "\n"
                + 'report = "report.json"'
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
    _expected_result: CheckConfiguration = CheckConfiguration(
        8,
        10,
        Path("report.json"),
        {Path("is_python_script/")},
        {Path("not_python_script/")},
    )
    _json_config: str = """\
    {
        "min_version": 8,
        "max_version": 10,
        "include": [
            "is_python_script/"
        ],
        "exclude": [
            "not_python_script/"
        ],
        "report": "report.json"
    }
    """
    _pyproject_config: str = """\
    [tool.PyCompatibility]
    min_version = 8
    max_version = 10
    include = ["is_python_script/"]
    exclude = ["not_python_script/"]
    report = "report.json"
    """
    _toml_config: str = """\
    min_version = 8
    max_version = 10
    include = ["is_python_script/"]
    exclude = ["not_python_script/"]
    report = "report.json"
    """

    def test_default(self) -> None:
        self.assertEqual(
            CheckConfiguration.from_dict({}),
            CheckConfiguration(None, None, None, set(), set()),
        )

    def test_from_dict(self) -> None:
        self.assertEqual(
            CheckConfiguration.from_dict(
                {
                    "min_version": 8,
                    "max_version": 10,
                    "include": ["is_python_script/"],
                    "exclude": ["not_python_script/"],
                    "report": "report.json",
                }
            ),
            self._expected_result,
        )

    def test_from_version_range(self) -> None:
        self.assertEqual(
            CheckConfiguration.from_dict(
                {
                    "version": ["8", "10"],
                    "include": ["is_python_script/"],
                    "exclude": ["not_python_script/"],
                    "report": "report.json",
                }
            ),
            self._expected_result,
        )

    def test_from_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(
                tmp_root / "Compat.json", mode="w", encoding="UTF-8"
            ) as fp:
                fp.write(self._json_config)
            self.assertEqual(
                CheckConfiguration.from_file(tmp_root / "Compat.json"),
                self._expected_result,
            )

    def test_from_toml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(
                tmp_root / "Compat.toml", mode="w", encoding="UTF-8"
            ) as fp:
                fp.write(self._toml_config)
            self.assertEqual(
                CheckConfiguration.from_file(tmp_root / "Compat.toml"),
                self._expected_result,
            )

    def test_from_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(
                tmp_root / "pyproject.toml", mode="w", encoding="UTF-8"
            ) as fp:
                fp.write(self._pyproject_config)
            self.assertEqual(
                CheckConfiguration.from_file(tmp_root / "pyproject.toml"),
                self._expected_result,
            )

    def test_invalid_configuration_file_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            Path.touch(tmp_root / "config.invalid_file_extension")
            with self.assertRaises(ReadConfigurationError):
                CheckConfiguration.from_file(
                    tmp_root / "config.invalid_file_extension"
                )

    def test_discover_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(
                tmp_root / "Compat.json", mode="w", encoding="UTF-8"
            ) as fp:
                fp.write(self._json_config)
            self.assertEqual(
                CheckConfiguration.discover(tmp_root), self._expected_result
            )

    def test_discover_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with open(
                tmp_root / "pyproject.toml", mode="w", encoding="UTF-8"
            ) as fp:
                fp.write(self._pyproject_config)
            self.assertEqual(
                CheckConfiguration.discover(tmp_root), self._expected_result
            )

    def test_no_configuration_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(CheckConfiguration.discover(Path(tmp)), None)

    def test_unused_configuration_warning(self) -> None:
        with redirect_log_with_config() as buf:
            CheckConfiguration.from_dict(
                {"version": ["8", "10"], "unused": "unused"}
            )
            self.assertEqual(
                buf.getvalue(),
                "[Warning] configuration: UnusedConfigurationWarning: Unused configuration: unused\n",
            )

    def test_configuration_file_path_not_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            with self.assertRaises(ReadConfigurationError):
                CheckConfiguration.from_file(tmp_root / "not_exist.json")
            with self.assertRaises(ReadConfigurationError):
                (tmp_root / "a_dir").mkdir()
                CheckConfiguration.from_file(tmp_root / "a_dir")

    def test_no_pyproject_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            pyproject_path: Path = tmp_root / "pyproject.toml"
            with open(pyproject_path, mode="w", encoding="UTF-8") as fp:
                fp.write(
                    """\
                    min_version=8
                    max_version = 10
                    include = ["is_python_script/"]
                    exclude = ["not_python_script/"]
                    report = "report.json"
                    """
                )
            with self.assertRaises(ParseConfigurationError):
                CheckConfiguration.from_file(pyproject_path)

    def test_no_pyproject_section_in_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            (tmp_root / "pyproject.toml").touch()
            self.assertEqual(CheckConfiguration.discover(tmp_root), None)

    def test_check_and_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root: Path = Path(tmp)
            (tmp_root / "pyfile1.py").touch()
            (tmp_root / "pyfile_dir1").mkdir()
            (tmp_root / "pyfile_dir2").mkdir()
            (tmp_root / "pyfile_dir1" / "pyfile2.py").touch()
            (tmp_root / "pyfile_dir2" / "pyfile3.py").touch()
            (tmp_root / "pyfile4.py").touch()
            (tmp_root / "report.json").touch()

            # min_version not an integer
            with self.assertRaises(ParseConfigurationError):
                CheckConfiguration(
                    None, 10, None, set(), set()
                ).check_and_resolve()

            # min_version > max_version
            with self.assertRaises(ParseConfigurationError):
                CheckConfiguration(
                    13, 10, None, set(), set()
                ).check_and_resolve()

            # Path resolving
            self.assertEqual(
                CheckConfiguration(
                    8,
                    10,
                    tmp_root / "report.json",
                    {
                        tmp_root / "pyfile1.py",
                        tmp_root / "pyfile_dir1" / "pyfile2.py",
                        tmp_root / "pyfile_dir2",
                    },
                    {tmp_root / "pyfile_dir1", tmp_root / "pyfile4.py"},
                ).check_and_resolve(),
                CheckConfiguration(
                    8,
                    10,
                    (tmp_root / "report.json").resolve(strict=True),
                    {
                        (tmp_root / "pyfile1.py").resolve(strict=True),
                        (tmp_root / "pyfile_dir2" / "pyfile3.py").resolve(
                            strict=True
                        ),
                    },
                    set(),
                ),
            )
