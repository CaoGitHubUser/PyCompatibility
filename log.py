from logging import *

import color


class ColoredStreamHandler(StreamHandler):  # type: ignore
    def format(self, record: LogRecord) -> str:
        # TODO: refactor this into match-case after Python 3.9 EOL
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
            return f"{color.FOREGROUND_COLOR.RED}Fatal Error: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
        else:
            return record.msg


def ensure_color_log() -> None:
    basicConfig(handlers=[ColoredStreamHandler()])
