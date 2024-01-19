"""
CLI of main program

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
import sys
from pathlib import Path
from typing import Optional, Set, Tuple

import click

from . import log

from .configuration import CheckConfiguration

if sys.version_info < (3, 10):
    import pkg_resources

    __version__: str = pkg_resources.get_distribution("PyCompatibility").version
else:
    import importlib.metadata

    __version__: str = importlib.metadata.version("PyCompatibility")
LOG: logging.Logger = logging.getLogger("CLI")


@click.group(
    no_args_is_help=True,
    context_settings={"help_option_names": ("--help", "-h")},
)
@click.pass_context
@click.option(
    "--log-level",
    type=str,
    help="The logging level.Logs lesser than this level will not be logged",
)
@click.option(
    "--configuration-path",
    "--cfg",
    type=Path,
    help="Specify path to the configuration file",
)
@click.version_option(version=__version__)
@log.handle_exception
def main(
    context: click.Context,
    log_level: Optional[str],
    configuration_path: Optional[Path],
) -> None:
    context.ensure_object(dict)
    context.obj["configuration"] = {
        "log_level": log_level,
        "configuration_path": configuration_path,
    }


@main.command
@click.pass_context
@click.argument(
    "include",
    nargs=-1,
    required=True,
    type=Path,
)
@click.option(
    "--log-level",
    type=str,
    help="The logging level.Logs lesser than this level will be ignored",
)
@click.option(
    "--configuration-path",
    "--cfg",
    type=Path,
    help="Specify path to the configuration file",
)
@click.option("--color/--no-color", help="Colorful output", default=True)
@click.option(
    "--min-version", "-minV", type=int, help="The min version to check"
)
@click.option(
    "--max-version", "-maxV", type=int, help="The max version to check"
)
@click.option(
    "--version", "-V", type=(int, int), help="The version range to check"
)
@click.option(
    "--exclude",
    multiple=True,
    type=Path,
    help="The files that PyCompatibility will not check",
)
@click.option(
    "--report",
    "-o",
    type=Path,
    help="The path to the file to write the JSON check report",
)
@log.handle_exception
def check(
    context: click.Context,
    log_level: Optional[str],
    configuration_path: Optional[Path],
    min_version: Optional[int],
    max_version: Optional[int],
    version: Optional[Tuple[int, int]],
    include: Optional[Tuple[Path, ...]],
    exclude: Optional[Tuple[Path, ...]],
    report: Optional[Path],
    color: bool,
) -> None:
    configuration_path = (
        configuration_path or context.obj["configuration"]["configuration_path"]
    )
    log.initialize(
        log_level or context.obj["configuration"]["log_level"], color
    )
    if configuration_path is None:
        file_configuration = CheckConfiguration.discover(Path("."))
    else:
        file_configuration = CheckConfiguration.from_file(configuration_path)
    include_set: Set[Path] = set(include) if include is not None else set()
    exclude_set: Set[Path] = set(exclude) if exclude is not None else set()

    if file_configuration is not None:
        min_version = min_version or file_configuration.min_version
        max_version = max_version or file_configuration.max_version
        report = report or file_configuration.report
        include_set.update(file_configuration.include or set())
        exclude_set.update(file_configuration.exclude or set())
    if version is not None:
        min_version = min_version or version[0]
        max_version = max_version or version[1]

    configuration: CheckConfiguration = CheckConfiguration.from_dict(
        {
            "min_version": min_version,
            "max_version": max_version,
            "report": report,
            "include": include_set,
            "exclude": exclude_set,
        }
    ).check_and_resolve()
    LOG.debug(f"Using configuration: {configuration}")


@main.command
@click.pass_context
@click.option(
    "--log-level",
    type=str,
    help="The logging level.Logs lesser than this level will not be logged",
)
@click.option("--color/--no-color", default=True, help="Enable colorful output")
@log.handle_exception
def cleanup(
    context: click.Context, log_level: Optional[str], color: bool
) -> None:
    log_level = log_level or context.obj["log_level"] or "INFO"
