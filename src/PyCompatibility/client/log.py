"""
Reconfig logging Handler to reformat the log message

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
from typing import Any, Callable, TextIO

from . import color
from .exception import PyCompatibilityException

SUCCESS: int = 25
LOG: logging.Logger = logging.getLogger("log")
_initialized: bool = False
color_support: bool = True


class ColoredStreamHandler(logging.StreamHandler):  # type: ignore[type-arg] # pragma: no cover
    def format(self, record: logging.LogRecord) -> str:
        # TODO: refactor this into match-case after EOL: Python 3.9
        if record.levelname == "DEBUG":
            return (
                f"{color.BACKGROUND_COLOR.CYAN}[Debug]{color.BACKGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.CYAN}{record.name}: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        if record.levelname == "INFO":
            return (
                f"{color.BACKGROUND_COLOR.BLUE}[Info]{color.BACKGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.BLUE}{record.name}: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        if record.levelname == "WARNING":
            return (
                f"{color.BACKGROUND_COLOR.YELLOW}{color.FOREGROUND_COLOR.BLACK}"
                f"[Warning]"
                f"{color.BACKGROUND_COLOR.DEFAULT}{color.FOREGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.YELLOW}{record.name}: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        if record.levelname == "ERROR":
            return (
                f"{color.BACKGROUND_COLOR.RED}[Error]{color.BACKGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.RED}{record.name}: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        if record.levelname == "CRITICAL":
            return (
                f"{color.FOREGROUND_COLOR.RED}"
                f"Fatal error: {record.name}: {record.msg}"
                f"{color.FOREGROUND_COLOR.DEFAULT}"
            )
        if record.levelname == "SUCCESS":
            return (
                f"{color.BACKGROUND_COLOR.GREEN}[Success]{color.BACKGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.GREEN}{record.name}: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        return f"{record.name}: {record.msg}"


class FormattedStreamHandler(logging.StreamHandler):  # type: ignore[type-arg]
    def format(self, record: logging.LogRecord) -> str:
        # TODO: refactor this into match-case after EOL: Python 3.9
        if record.levelname == "DEBUG":
            return f"[Debug] {record.name}: {record.msg}"
        if record.levelname == "INFO":
            return f"[Info] {record.name}: {record.msg}"
        if record.levelname == "WARNING":
            return f"[Warning] {record.name}: {record.msg}"
        if record.levelname == "ERROR":
            return f"[Error] {record.name}: {record.msg}"
        if record.levelname == "SUCCESS":
            return f"[Success] {record.name}: {record.msg}"
        if record.levelname == "CRITICAL":
            return f"Fatal error: {record.name}: {record.msg}"
        return f"{record.name}: {record.msg}"


if sys.platform == "win32":
    # Ensure ANSI escape code enabled
    import ctypes

    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:  # pragma: no cover
        color_support = False


def config_with_colored_handler(**kwargs: Any) -> None:  # pragma: no cover
    handlers = list(kwargs.pop("handlers", []))
    stream = kwargs.pop("stream", None)
    handlers.append(ColoredStreamHandler(stream=stream))
    kwargs["handlers"] = handlers
    logging.basicConfig(**kwargs)


def config_with_formatted_handler(**kwargs: Any) -> None:
    handlers = kwargs.pop("handlers", [])
    stream = kwargs.pop("stream", None)
    handlers.append(FormattedStreamHandler(stream=stream))
    kwargs["handlers"] = handlers
    logging.basicConfig(**kwargs)


def success(
    msg: object,
    *args: object,
    logger: logging.Logger = logging.root,
    **kwargs: Any,
) -> None:
    logger.log(SUCCESS, msg, *args, **kwargs)


def initialize(
    log_level: str, enable_color: bool, stream: TextIO = sys.stdout
) -> None:
    global _initialized
    if _initialized:
        LOG.debug("Already initialized, skipping.")
        return
    logging.addLevelName(SUCCESS, "SUCCESS")
    logging.basicConfig(
        handlers=(ColoredStreamHandler(stream=stream),)
        if enable_color and color_support
        else (FormattedStreamHandler(stream=stream),),
        level=log_level,
    )
    _initialized = True


def handle_exception(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator to handle the exception when call a command or group
    """

    def decor(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except PyCompatibilityException as handled_exception:
            if handled_exception.__traceback__ is not None:
                logger = logging.getLogger(
                    f'{handled_exception.__traceback__.tb_frame.f_globals["__name__"]}: {handled_exception.__class__.__name__}'
                )
            else:
                logger = logging.getLogger(handled_exception.__class__.__name__)
            logger.error(handled_exception)
        except Exception as uncaught_exception:
            if uncaught_exception.__traceback__ is not None:
                logger = logging.getLogger(
                    f'{uncaught_exception.__traceback__.tb_frame.f_globals["__name__"]}: {uncaught_exception.__class__.__name__}'
                )
            else:
                logger = logging.getLogger(
                    uncaught_exception.__class__.__name__
                )
            logger.critical(uncaught_exception)

    decor.__name__ = func.__name__
    return decor
