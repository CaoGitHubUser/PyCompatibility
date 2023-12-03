"""
BaseException, Exception, Warning ans some useful exception tools for the whole program

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

from typing import Optional, Type, Union

from . import log


class BasePyCompatibilityException(BaseException):
    pass


class PyCompatibilityException(Exception, BasePyCompatibilityException):
    pass


class PyCompatibilityWarning(Warning, BasePyCompatibilityException):
    pass


def static_assert(
    assertion: bool,
    exc: Union[Type[Exception], Exception] = PyCompatibilityException,
    msg: str = "",
) -> None:
    """An assertion function that can raise specified exception"""
    if isinstance(exc, Exception):
        if msg:
            raise ValueError("Both exception instance and message are given!")
    else:
        exc = exc(msg)
    if not assertion:
        raise exc


def warn(
    message: Union[str, Warning],
    category: Optional[Type[Warning]] = None,
    stacklevel: int = 1,
) -> None:
    if isinstance(message, Warning):
        category = message.__class__
    else:
        category = category or UserWarning
    log.warning(f"{category.__name__}: {str(message)}", stacklevel=stacklevel)
