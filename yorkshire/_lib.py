#!/usr/bin/env python3

import ast
import configparser
import os.path
import logging
import tempfile
import json
from typing import Generator
from typing import Optional
from typing import Tuple

import requests
import tomli
from pip_requirements_parser import RequirementsFile
from pip_requirements_parser import OptionLine
from urllib.parse import urlparse

from .exceptions import UnknownFileError
from .exceptions import DownloadFileError
from .exceptions import FileParseError
from .exceptions import GithubRateLimitError

_LOGGER = logging.getLogger(__name__)


def _detect_pyproject_toml(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a pyproject.toml file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in pyproject.toml file located at %r", os.path.dirname(real_filepath) or ".")

    try:
        with open(filepath, "rb") as f:
            content = tomli.load(f)
    except Exception as exc:
        raise FileParseError(f"Failed to open and parse pyproject.toml file {real_filepath!r}: {str(exc)}") from exc

    # Check Poetry configuration.
    poetry_source = ((content.get("tool") or {}).get("poetry") or {}).get("source") or []
    if len(poetry_source) > 0:
        _LOGGER.warning(
            "File %r uses an explicitly configured Poetry source: %s",
            real_filepath,
            [i["url"] for i in poetry_source],
        )
        return False

    # Check PDM configuration.
    poetry_source = ((content.get("tool") or {}).get("pdm") or {}).get("source") or []
    if len(poetry_source) > 0:
        _LOGGER.warning(
            "File %r uses an explicitly configured PDM source: %s",
            real_filepath,
            [i["url"] for i in poetry_source],
        )
        return False

    return True


def _detect_setup_cfg(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a setup.cfg file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in setup.cfg file located at %r", os.path.dirname(real_filepath) or ".")

    config = configparser.ConfigParser()
    config.read(filepath)

    dependency_links = config["options"].get("dependency_links")
    if dependency_links is not None:
        _LOGGER.warning("File %r uses dependency links: %s", real_filepath, dependency_links)
        return False

    return True


def _detect_setup_py(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a setup.py file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in setup.py file located at %r", os.path.dirname(real_filepath) or ".")

    try:
        with open(filepath) as f:
            content = f.read()
    except Exception as exc:
        raise FileParseError(f"Failed to open setup.py file {real_filepath!r}: {str(exc)}") from exc

    tree = ast.parse(content)
    for item in tree.body:
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Call):
            for kwarg in item.value.keywords:
                if kwarg.arg == "dependency_links":
                    _LOGGER.warning("File %r uses dependency links", real_filepath)
                    return False

    return True


def _detect_pipfile(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a Pipfile file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in Pipfile file located at %r", os.path.dirname(real_filepath) or ".")

    try:
        with open(filepath, "rb") as f:
            content = tomli.load(f)
    except Exception as exc:
        raise FileParseError(f"Failed to open and parse Pipfile file {real_filepath!r}: {str(exc)}") from exc

    sources = content.get("source") or []
    if len(sources) > 1:
        _LOGGER.warning(
            "File %r states one or multiple Python package indexes: %s",
            real_filepath,
            [i["url"] for i in sources],
        )
        return False

    return True


def _detect_pipfile_lock(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a Pipfile.lock file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in Pipfile.lock file located at %r", os.path.dirname(real_filepath) or ".")

    with open(filepath) as f:
        content = json.load(f)

    sources = content["_meta"]["sources"]
    if len(sources) > 1:
        _LOGGER.warning(
            "File %r states one or multiple Python package indexes: %s",
            filepath,
            [i["url"] for i in sources],
        )
        return False

    return True


def _detect_requirements(filepath: str, *, real_path: str) -> bool:
    """Check requirements.{txt,in} files for a possible dependency confusion."""
    try:
        items = RequirementsFile.parse(filepath, include_nested=True, is_constraint=False)
    except Exception as exc:
        raise FileParseError(f"Failed to parse requirements file {real_path!r}: {str(exc)}") from exc

    for item in items:
        if isinstance(item, OptionLine):
            extra_index_urls = item.options.get("extra_index_urls")
            if extra_index_urls is not None:
                _LOGGER.warning("File %r states one or multiple extra index URLs: %s", real_path, extra_index_urls)
                return False

            find_links = item.options.get("find_links")
            if find_links is not None:
                _LOGGER.warning("File %r states --find-links: %r", real_path, find_links)
                return False

    return True


def _detect_requirements_in(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a requirements.in file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in requirements.in file located at %r", os.path.dirname(real_filepath) or ".")
    return _detect_requirements(filepath, real_path=real_filepath)


def _detect_requirements_txt(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a requirements.txt file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in requirements.txt file located at %r", os.path.dirname(real_filepath) or ".")
    return _detect_requirements(filepath, real_path=real_filepath)


def _detect_pdm_lock(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in a pdm.lock file."""
    real_filepath = _real_path or filepath
    _LOGGER.info("Performing detection in pdm.lock file located at %r", os.path.dirname(real_filepath) or ".")

    try:
        with open(filepath, "rb") as f:
            content = tomli.load(f)
    except Exception as exc:
        raise FileParseError(f"Failed to open and parse pdm.lock file {real_filepath!r}: {str(exc)}") from exc

    okay = True
    for package_name, file_entry in content["metadata"]["files"].items():
        for entry in file_entry:
            if not entry["url"].startswith("https://files.pythonhosted.org/"):
                _LOGGER.warning("Package %r is not consumed from PyPI: %s", package_name, entry["url"])
                okay = False

    return okay


_FILE_NAMES = {
    "pyproject.toml": _detect_pyproject_toml,
    "setup.cfg": _detect_setup_cfg,
    "setup.py": _detect_setup_py,
    "Pipfile": _detect_pipfile,
    "Pipfile.lock": _detect_pipfile_lock,
    "requirements.txt": _detect_requirements_txt,
    "requirements.in": _detect_requirements_in,
    "pdm.lock": _detect_pdm_lock,
}


def detect_file(filepath: str, *, _real_path: Optional[str] = None) -> bool:
    """Detect possible dependency confusion in the given file."""
    file_name = os.path.basename(_real_path or filepath)

    handler = _FILE_NAMES.get(file_name)
    if handler is None:
        raise UnknownFileError(f"Unknown requirements file {file_name!r}, supported are {list(_FILE_NAMES.keys())!r}")

    return handler(filepath, _real_path=_real_path)


def detect(path: str) -> Generator[Tuple[str, bool], None, None]:
    """Detect possible dependency confusion in the specified path.

    @param path: A directory, file, or URL. The tool traverses the given directory structure, if a directory.
    @return: True if no possible issue was found, otherwise false.
    """
    if os.path.isdir(path):
        _LOGGER.debug("Listing files in directory %r", path)
        for directory, _, files in os.walk(path, topdown=False):
            for file_name in files:
                if file_name in _FILE_NAMES:
                    filepath = os.path.join(directory, file_name)
                    yield filepath, detect_file(filepath)
        return None
    elif os.path.isfile(path):
        _LOGGER.debug("Checking file %r", path)
        yield path, detect_file(path)
        return None
    elif path.startswith(("https://", "http://")):
        url = path
        path = urlparse(url)._replace(query="", params="", fragment="").geturl()
        _LOGGER.debug("Downloading from %r", path)
        response = requests.get(url)
        if response.status_code == 403 and (urlparse(url).netloc in ("github.com", "githubusercontent.com")):
            raise GithubRateLimitError(f"Unable to download {path} due to rate limit ({response.status_code}): {response.text}")
        if response.status_code == 404:
            raise DownloadFileError(f"{path} not found, check full path ({response.status_code}): {response.text}")
        if response.status_code != 200:
            raise DownloadFileError(f"Unable to download {path}: ({response.status_code}): {response.text}")

        with tempfile.NamedTemporaryFile(mode="w") as tmpfile:
            with open(tmpfile.name, "w") as f:
                f.write(response.text)

            yield path, detect_file(tmpfile.name,  _real_path=path)
            return None
    else:
        raise UnknownFileError(f"The given path {path} is not a file, directory or URL")
