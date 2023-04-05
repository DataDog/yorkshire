#!/usr/bin/env python3

import os
from typing import Generator

import pytest
from yorkshire import detect_file

from base import Base

ALLOWED_INDEXES = {
    "https://my.allowed.index.org/simple",
    'https://pypi.org/simple',
}

def _iter_files(directory: str) -> Generator[str, None, None]:
    """Create a generator yielding all the files in the specified directory."""
    for root, _, files in os.walk(directory):
        for file_name in files:
            yield os.path.join(root, file_name)


class TestDetectFile(Base):
    """Test detecting on a file level."""

    @pytest.mark.parametrize("filepath", list(_iter_files(os.path.join(Base.DATA_DIR, "requirements_files", "okay"))))
    def test_okay(self, filepath: str) -> None:
        """Test all the successful scenarios."""
        assert detect_file(filepath) is True, \
            f"Test case for {filepath!r} should NOT be vulnerable to dependency confusion"

    @pytest.mark.parametrize("filepath", list(_iter_files(os.path.join(Base.DATA_DIR, "requirements_files", "fail"))))
    def test_fail(self, filepath: str, index_allowlist: bool) -> None:
        """Test all the failing scenarios."""

        kwargs = { 'allowed_indexes': ALLOWED_INDEXES } if index_allowlist else {}

        assert detect_file(filepath, **kwargs) is False, \
            f"Test case for {filepath!r} should be vulnerable to dependency confusion"

    @pytest.mark.parametrize("filepath", list(_iter_files(os.path.join(Base.DATA_DIR, "with_allowed_indexes", "okay"))))
    def test_allowlist_okay(self, filepath: str) -> None:
        """test all the successful scenarios with allowed indexes."""
        assert detect_file(filepath, allowed_indexes=ALLOWED_INDEXES) is True, \
            f"Test case for {filepath!r} should NOT be vulnerable to dependency confusion"
