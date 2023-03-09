#!/usr/bin/env python3

from click.testing import CliRunner
from yorkshire.cli import cli
import yorkshire

from base import Base


class TestCLI(Base):
    """Test invocation of the CLI."""

    def test_version(self):
        """Test obtaining a CLI version."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert result.output == f"{yorkshire.__title__}: {yorkshire.__version__}\n"

    def test_help(self) -> None:
        """Test obtaining a help message."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
