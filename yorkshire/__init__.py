#!/usr/bin/env python3

from .__about__ import __version__
from ._lib import detect
from ._lib import detect_file
from .exceptions import YorkshireException

__author__ = "Fridolin Pokorny <fridolin.pokorny@datadoghq.com>"
__title__ = "yorkshire"

__all__ = [
    "__version__",
    YorkshireException.__name__,
    detect.__name__,
    detect_file.__name__,
]
