#!/usr/bin/env python3


class YorkshireException(Exception):
    """A base class for the exception hierarchy."""


class UnknownFileError(YorkshireException):
    """An exception raised when the given path is not known."""


class DownloadFileError(YorkshireException):
    """An exception raised when the given file was not downloadable."""


class FileParseError(YorkshireException):
    """An exception raised when cannot parse the given requirements file."""

class GithubRateLimitError(DownloadFileError):
    """An exception was raised while downloading a remote requirments file because of rate limiting from Github."""