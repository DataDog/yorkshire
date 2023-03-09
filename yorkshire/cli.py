#!/usr/bin/env python3

import logging

import yorkshire
import rich_click as click
import daiquiri


_LOGGER = daiquiri.getLogger(yorkshire.__title__)
daiquiri.setup(level=logging.INFO)


def _print_version(ctx: click.core.Context, _: click.core.Option, value: str) -> None:
    """Print version and exit."""
    if not value or ctx.resilient_parsing:
        return

    click.echo(f"{yorkshire.__title__}: {yorkshire.__version__}")
    ctx.exit(0)


@click.group()
@click.option(
    "--debug/--no-debug",
    default=False,
    help="Run this tool in a debug mode.",
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    is_eager=True,
    callback=_print_version,
    expose_value=False,
    help="Print version and exit.",
)
def cli(debug: bool = False) -> None:
    """Detect a possibility to have a dependency confusion in your Python dependencies."""
    if debug:
        _LOGGER.setLevel(logging.DEBUG)
        _LOGGER.debug("Debug mode is on")


@cli.command("detect")
@click.pass_context
@click.argument(
    "path",
    type=str,
    metavar="FILE|URL|DIR",
)
def cli_detect(ctx: click.core.Context, path: str) -> None:
    """Check for a possible dependency confusion in a requirements file, files in a directory, or a URL."""
    okay = yorkshire.detect(path)
    ctx.exit(not okay)


__name__ == "__main__" and cli(auto_envvar_prefix=yorkshire.__title__.upper())
