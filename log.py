import logging

import color


class ColoredStreamHandler(logging.StreamHandler):  # type: ignore
    def format(self, record: logging.LogRecord) -> str:
        # TODO: refactor this into match-case after Python 3.9 EOL
        if record.levelname == "DEBUG":
            return f"{color.BACKGROUND_COLOR.CYAN}[Debug]{color.BACKGROUND_COLOR.DEFAULT} {record.msg}"
        elif record.levelname == "INFO":
            return f"{color.BACKGROUND_COLOR.BLUE}[Info]{color.BACKGROUND_COLOR.DEFAULT} {record.msg}"
        elif record.levelname == "WARNING":
            return f"{color.BACKGROUND_COLOR.YELLOW}[Warning]{color.BACKGROUND_COLOR.DEFAULT} {record.msg}"
        elif record.levelname == "ERROR":
            return f"{color.BACKGROUND_COLOR.RED}[Error]{color.BACKGROUND_COLOR.DEFAULT} {record.msg}"
        elif record.levelname == "CRITICAL":
            return f"{color.FOREGROUND_COLOR.RED}Fatal Error: {record.msg}{color.FOREGROUND_COLOR.DEFAULT}"
        else:
            return record.msg


def ensure_color_log() -> None:
    logging.basicConfig(handlers=[ColoredStreamHandler()])
