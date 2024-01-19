"""
Defines Read/Write configuration of the PyCompatibility and the configuration exceptions

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

import dataclasses
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Set

import tomli
import tomli_w

from . import exception

LOG: logging.Logger = logging.getLogger("configuration")


class BaseConfigurationException(exception.BasePyCompatibilityException):
    pass


class ConfigurationException(
    exception.PyCompatibilityException, BaseConfigurationException
):
    pass


class ReadConfigurationError(ValueError, ConfigurationException):
    pass


class WriteConfigurationError(ValueError, ConfigurationException):
    pass


class ParseConfigurationError(ValueError, ConfigurationException):
    pass


class UnusedConfigurationWarning(
    UserWarning, exception.PyCompatibilityWarning, BaseConfigurationException
):
    pass


@dataclasses.dataclass(frozen=True)
class CheckConfiguration:
    min_version: Optional[int]
    max_version: Optional[int]
    report: Optional[Path]
    include: Set[Path]
    exclude: Set[Path]

    @classmethod
    def from_dict(cls, dict_config: Dict[str, Any]) -> "CheckConfiguration":
        min_version = dict_config.pop("min_version", None)
        max_version = dict_config.pop("max_version", None)
        version = dict_config.pop("version", None)
        if (min_version is None or max_version is None) and isinstance(
            version, (list, tuple)
        ):
            exception.assert_exc(
                len(version) == 2,
                ParseConfigurationError("`version` should have two elements!"),
            )
            if min_version is None:
                min_version = version[0]
            if max_version is None:
                max_version = version[1]
        min_version = None if min_version is None else int(min_version)
        max_version = None if max_version is None else int(max_version)

        report: Optional[Path] = dict_config.pop("report", None)
        if report is not None:
            report = Path(report)

        include = set(Path(path) for path in dict_config.pop("include", ()))
        exclude = set(Path(path) for path in dict_config.pop("exclude", ()))

        if dict_config:
            exception.warn(
                f"Unused configuration: {' '.join(dict_config.keys())}",
                UnusedConfigurationWarning,
                logger=LOG,
            )

        return cls(
            min_version=min_version,
            max_version=max_version,
            report=report,
            include=include,
            exclude=exclude,
        )

    @classmethod
    def from_file(cls, path: Path) -> "CheckConfiguration":
        if not path.is_file():
            raise ReadConfigurationError("Configuration path is not a file!")
        # TODO: refactor this into match-case after EOL: Python 3.9
        if path.suffix == ".toml":
            dict_config = tomli.loads(path.read_text(encoding="UTF-8"))
        elif path.suffix == ".json":
            dict_config = json.loads(path.read_text(encoding="UTF-8"))
        else:
            raise ReadConfigurationError(
                "Configuration path should be a `.toml` or `.json`!"
            )

        if path.name == "pyproject.toml":
            try:
                dict_config = dict_config["tool"]["PyCompatibility"]
            except KeyError:
                raise ParseConfigurationError(
                    "No `[tool.PyCompatibility]` section in `pyproject.toml`"
                )

        return cls.from_dict(dict_config)

    def serialize(self) -> Dict[str, Any]:
        return {
            "min_version": self.min_version,
            "max_version": self.max_version,
            "report": self.report,
            "include": self.include,
            "exclude": self.exclude,
        }

    def to_file(self, path: Path) -> None:
        dict_config = self.serialize()
        # Make it JSON/TOML serializable
        dict_config["include"] = tuple(dict_config["include"])
        dict_config["exclude"] = tuple(dict_config["exclude"])
        dict_config["report"] = str(dict_config["report"])

        if path.name == "pyproject.toml":
            with open(path, mode="a", encoding="UTF-8") as fp:
                if (
                    path.read_text(encoding="UTF-8")
                    .replace("\r", "\n")
                    .endswith("\n")
                ):
                    fp.write("\n")
                fp.write(
                    "[tool.PyCompatibility]\n" f"{tomli_w.dumps(dict_config)}"
                )
        elif path.suffix == ".json":
            with open(path, mode="w", encoding="UTF-8") as fp:
                json.dump(dict_config, fp, sort_keys=True, indent=4)
        elif path.suffix == ".toml":
            with open(path, mode="w", encoding="UTF-8") as fp:
                fp.write(tomli_w.dumps(dict_config))
        else:
            raise WriteConfigurationError(
                "PyCompatibility currently only support `.json` and `.toml` configuration file."
                f"The file you give has suffix {path.suffix}"
            )

    @classmethod
    def discover(cls, path: Path) -> Optional["CheckConfiguration"]:
        configuration: Optional["CheckConfiguration"] = None
        json_config_file = path / "Compat.json"
        pyproject_config_file = path / "pyproject.toml"
        if json_config_file.is_file():
            configuration = cls.from_file(json_config_file)
        if configuration is None and pyproject_config_file.is_file():
            toml_config = tomli.loads(
                pyproject_config_file.read_text(encoding="UTF-8")
            )
            try:
                configuration = cls.from_dict(
                    toml_config["tool"]["PyCompatibility"]
                )
            except KeyError:
                pass
        return configuration

    def check_and_resolve(self) -> "CheckConfiguration":
        if not isinstance(self.min_version, int) or not isinstance(
            self.max_version, int
        ):
            raise ParseConfigurationError(
                "No min and/or max version specified!"
            )
        exception.assert_exc(
            self.min_version <= self.max_version,
            ParseConfigurationError(
                "min_version should less than or equal max_version"
            ),
        )
        include: Set[Path] = set()
        exclude: Set[Path] = set()
        for path in self.include:
            exception.assert_exc(
                path.exists(),
                ParseConfigurationError(f"include path {path} doesn't exist!"),
            )
            path = path.resolve(strict=True)
            if path.is_file():
                include.add(path)
            else:
                for dir_path, _, filenames in os.walk(path):
                    include.update(
                        Path(f"{dir_path}/{filename}") for filename in filenames
                    )
        include = set(path.resolve(strict=True) for path in include)

        for path in self.exclude:
            exception.assert_exc(
                path.exists(),
                ParseConfigurationError(f"exclude path {path} doesn't exist!"),
            )
            path = path.resolve(strict=True)
            if path.is_file():
                exclude.add(path)
            else:
                for dir_path, _, filenames in os.walk(path):
                    exclude.update(
                        Path(f"{dir_path}/{filename}") for filename in filenames
                    )
        exclude = set(path.resolve(strict=True) for path in exclude)
        include -= exclude

        if (report := self.report) is not None:
            report = report.resolve(strict=True)
        return CheckConfiguration(
            min_version=self.min_version,
            max_version=self.max_version,
            report=report,
            include=include,
            exclude=set(),
        )
