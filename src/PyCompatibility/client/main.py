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

import importlib.metadata
import logging
from pathlib import Path
from typing import Any, Callable, cast, Optional, Set, Tuple

import click

from . import log
from .configuration import CheckConfiguration

__version__: str = importlib.metadata.version("PyCompatibility")
__license_file__: str = (
    importlib.metadata.metadata("PyCompatibility").get("License-File")
    or "COPYING"
)
__license__: str = cast(
    Callable[[str], str],
    importlib.metadata.distribution("PyCompatibility").read_text,
)(__license_file__)

LOG: logging.Logger = logging.getLogger("CLI")

DISCLAIMER_OF_WARRANTY: str = """\
                    Disclaimer of Warranty
  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
"""

# Yes, it is a trick...
TERMS_AND_CONDITIONS: str = (
    "                       TERMS AND CONDITIONS"
    + __license__.split("TERMS AND CONDITIONS")[1].split(
        "END OF TERMS AND CONDITIONS"
    )[0]
    + "END OF TERMS AND CONDITIONS"
    + "\n"
)


def _print_notice(func: Callable[..., Any]) -> Callable[..., Any]:
    def decor(*args: Any, **kwargs: Any) -> Any:
        print(
            "PyCompatibility  Copyright (C) 2023-2024  Bo Wen Cao" + "\n"
            "This program comes with ABSOLUTELY NO WARRANTY; for details type `show-license --warranty-disclaimer'."
            + "\n"
            "This is free software, and you are welcome to redistribute it"
            + "\n"
            "under certain conditions; type `show-license --terms-and-conditions' for details."
            + "\n"
        )
        func(*args, **kwargs)

    return decor


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
@_print_notice
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
        file_configuration = CheckConfiguration.discover(Path(""))
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


@main.command(name="show-license")
@click.pass_context
@click.option(
    "--log-level",
    type=str,
    help="The logging level.Logs lesser than this level will not be logged",
)
@click.option("--color/--no-color", default=True, help="Enable colorful output")
@click.option(
    "--warranty-disclaimer", is_flag=True, help="Show disclaimer of warranty"
)
@click.option(
    "--terms-and-conditions", is_flag=True, help="Show terms and conditions"
)
@log.handle_exception
def show_license(
    context: click.Context,
    log_level: str,
    color: bool,
    warranty_disclaimer: bool,
    terms_and_conditions: bool,
) -> None:
    log.initialize(
        log_level or context.obj["configuration"]["log_level"], color
    )
    if terms_and_conditions:
        click.echo_via_pager(TERMS_AND_CONDITIONS)
    if warranty_disclaimer:
        click.echo_via_pager(DISCLAIMER_OF_WARRANTY)
