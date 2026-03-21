import logging
import os
from pathlib import Path
from shutil import which

from invoke import task

logger = logging.getLogger(__name__)
level = logging.INFO
logger.setLevel(level)
console_handler = logging.StreamHandler()
console_handler.setLevel(level)
logger.addHandler(console_handler)

PKG_NAME = "oembed"
PKG_PATH = Path(f"pelican/plugins/{PKG_NAME}")

ACTIVE_VENV = os.environ.get("VIRTUAL_ENV", None)
VENV_HOME = Path(os.environ.get("WORKON_HOME", "~/.local/share/virtualenvs"))
VENV_PATH = Path(ACTIVE_VENV) if ACTIVE_VENV else (VENV_HOME.expanduser() / PKG_NAME)
VENV = str(VENV_PATH.expanduser())
BIN_DIR = "bin" if os.name != "nt" else "Scripts"
VENV_BIN = Path(VENV) / Path(BIN_DIR)

UV = which("uv") or "uv"
CMD_PREFIX = f"{VENV_BIN}/" if ACTIVE_VENV else f"{UV} run "
PRECOMMIT = which("pre-commit") if which("pre-commit") else f"{CMD_PREFIX}pre-commit"
PTY = os.name != "nt"


@task
def tests(c, deprecations=False):
    """Run the test suite, optionally with `--deprecations`."""
    deprecations_flag = "" if deprecations else "-W ignore::DeprecationWarning"
    c.run(f"{CMD_PREFIX}pytest {deprecations_flag}", pty=PTY)


@task
def format(c, check=False, diff=False):
    """Run Ruff's auto-formatter, optionally with `--check` or `--diff`."""
    check_flag, diff_flag = "", ""
    if check:
        check_flag = "--check"
    if diff:
        diff_flag = "--diff"
    c.run(f"{CMD_PREFIX}ruff format {check_flag} {diff_flag} {PKG_PATH} tasks.py", pty=PTY)


@task
def ruff(c, concise=False, fix=False, diff=False):
    """Run Ruff to ensure code meets project standards."""
    concise_flag, fix_flag, diff_flag = "", "", ""
    if concise:
        concise_flag = "--output-format=concise"
    if fix:
        fix_flag = "--fix"
    if diff:
        diff_flag = "--diff"
    c.run(f"{CMD_PREFIX}ruff check {concise_flag} {diff_flag} {fix_flag} .", pty=PTY)


@task
def lint(c, concise=False, fix=False, diff=False):
    """Check code style via linting tools."""
    ruff(c, concise=concise, fix=fix, diff=diff)
    format(c, check=(not fix), diff=diff)


@task
def precommit(c):
    """Install pre-commit hooks to .git/hooks/pre-commit."""
    logger.info("** Installing pre-commit hooks **")
    c.run(f"{PRECOMMIT} install")


@task
def setup(c):
    """Set up the development environment."""
    if which("uv"):
        c.run(f"{UV} sync --group dev", pty=PTY)
        precommit(c)
        logger.info("\nDevelopment environment should now be set up and ready!\n")
    else:
        raise SystemExit(
            "uv is not installed. See https://docs.astral.sh/uv/getting-started/installation/"
        )
