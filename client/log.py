"""
Reconfig logging Handler to reformat the log message

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

import sys
from logging import *
from typing import Any

from . import color


class ColoredStreamHandler(StreamHandler):  # type: ignore[type-arg] # pragma: no cover
    def format(self, record: LogRecord) -> str:
        # TODO: refactor this into match-case after EOL: Python 3.9
        if record.levelname == "DEBUG":
            return (
                f"{color.BACKGROUND_COLOR.CYAN}[Debug]{color.BACKGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.CYAN}{record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        elif record.levelname == "INFO":
            return (
                f"{color.BACKGROUND_COLOR.BLUE}[Info]{color.BACKGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.BLUE}{record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        elif record.levelname == "WARNING":
            return (
                f"{color.BACKGROUND_COLOR.YELLOW}{color.FOREGROUND_COLOR.BLACK}"
                f"[Warning]"
                f"{color.BACKGROUND_COLOR.DEFAULT}{color.FOREGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.YELLOW}{record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        elif record.levelname == "ERROR":
            return (
                f"{color.BACKGROUND_COLOR.RED}[Error]{color.BACKGROUND_COLOR.DEFAULT} "
                f"{color.FOREGROUND_COLOR.RED}{record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
            )
        elif record.levelname == "CRITICAL":
            return f"{color.FOREGROUND_COLOR.RED}Fatal error: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
        else:
            return record.msg


class FormattedStreamHandler(StreamHandler):  # type: ignore[type-arg]
    def format(self, record: LogRecord) -> str:
        # TODO: refactor this into match-case after EOL: Python 3.9
        if record.levelname == "DEBUG":
            return f"[Debug] {record.msg}"
        elif record.levelname == "INFO":
            return f"[Info] {record.msg}"
        elif record.levelname == "WARNING":
            return f"[Warning] {record.msg}"
        elif record.levelname == "ERROR":
            return f"[Error] {record.msg}"
        elif record.levelname == "CRITICAL":
            return f"Fatal error: {record.msg}"
        else:
            return record.msg


if sys.platform == "win32":
    # Ensure ANSI escape code enabled
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    del ctypes


def config_with_colored_handler(**kwargs: Any) -> None:  # pragma: no cover
    handlers = list(kwargs.pop("handlers", []))
    stream = kwargs.pop("stream", None)
    handlers.append(ColoredStreamHandler(stream=stream))
    kwargs["handlers"] = handlers
    basicConfig(**kwargs)


def config_with_formatted_handler(**kwargs: Any) -> None:
    handlers = kwargs.pop("handlers", [])
    stream = kwargs.pop("stream", None)
    handlers.append(FormattedStreamHandler(stream=stream))
    kwargs["handlers"] = handlers
    basicConfig(**kwargs)


# Not for export
del sys
