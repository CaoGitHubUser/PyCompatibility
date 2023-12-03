"""
Defines Read/Write configuration of the PyCompatibility and the configuration exceptions

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

import dataclasses
import json
from pathlib import Path
from typing import Any, Dict, Literal, Tuple

import tomli
import tomli_w

from . import exception


class BaseConfigurationException(exception.BasePyCompatibilityException):
    pass


class ConfigurationException(Exception, BaseConfigurationException):
    pass


class ReadConfigurationError(ValueError, ConfigurationException):
    pass


class WriteConfigurationError(ValueError, ConfigurationException):
    pass


class ParseConfigurationError(ValueError, ConfigurationException):
    pass


class UnusedConfigurationWarning(UserWarning, BaseConfigurationException):
    pass


@dataclasses.dataclass(frozen=True)
class Configuration:
    debug: bool


@dataclasses.dataclass(frozen=True)
class CheckConfiguration(Configuration):
    min_version: int
    max_version: int
    output: Literal["text", "json"]
    include: Tuple[Path, ...]
    exclude: Tuple[Path, ...]

    @classmethod
    def from_dict(cls, dict_config: Dict[str, Any]) -> "CheckConfiguration":
        min_version = dict_config.pop("min_version", None)
        max_version = dict_config.pop("max_version", None)
        version = dict_config.pop("version", None)
        if min_version is None and max_version is None:
            exception.static_assert(
                version is not None,
                ParseConfigurationError(
                    "No `min_version` and/or `max_version` specified!"
                ),
            )
            exception.static_assert(
                isinstance(version, (list, tuple)),
                ParseConfigurationError("`version` should be a tuple or a list!"),
            )
            exception.static_assert(
                len(version) == 2,
                ParseConfigurationError("`version` should have two elements!"),
            )
            if min_version is None:
                min_version = version[0]
            if max_version is None:
                max_version = version[1]
        min_version = int(min_version)
        max_version = int(max_version)
        exception.static_assert(
            min_version <= max_version,
            ParseConfigurationError(
                "min_version should lesser or equal than max_version"
            ),
        )

        debug: bool = dict_config.pop("debug", False)

        output: Literal["json", "text"] = dict_config.pop("output", "text")
        exception.static_assert(
            output in ("text", "json"),
            ParseConfigurationError(
                f"Expected `text` or `json` for argument `output`, got {output}"
            ),
        )

        include: Tuple[Path, ...] = tuple(
            Path(path) for path in dict_config.pop("include", ())
        )
        exclude: Tuple[Path, ...] = tuple(
            Path(path) for path in dict_config.pop("exclude", ())
        )

        if dict_config:
            exception.warn(
                f"Unused configuration: {' '.join(dict_config.keys())}",
                UnusedConfigurationWarning,
            )

        return cls(
            debug=debug,
            min_version=min_version,
            max_version=max_version,
            output=output,
            include=include,
            exclude=exclude,
        )

    @classmethod
    def from_file(cls, path: Path) -> "CheckConfiguration":
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
            dict_config = dict_config["tool"]["PyCompatibility"]

        return cls.from_dict(dict_config)

    def serialize(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "min_version": self.min_version,
            "max_version": self.max_version,
            "output": self.output,
            "include": self.include,
            "exclude": self.exclude,
        }

    def to_file(self, path: Path) -> None:
        dict_config = self.serialize()
        if path.name == "pyproject.toml":
            with open(path, mode="a", encoding="UTF-8") as fp:
                if path.read_text(encoding="UTF-8").replace("\r", "\n").endswith("\n"):
                    fp.write("\n")
                fp.write("[tool.PyCompatibility]\n" f"{tomli_w.dumps(dict_config)}")
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
