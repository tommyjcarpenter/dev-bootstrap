import click
from datetime import datetime


def _ts():
    return datetime.now().strftime("%H:%M:%S")


def header(msg):
    ts = _ts()
    click.echo(click.style(f"\n{'=' * 60}", fg="cyan", bold=True))
    click.echo(click.style(f"  [{ts}] {msg}", fg="cyan", bold=True))
    click.echo(click.style(f"{'=' * 60}", fg="cyan", bold=True))


def info(msg):
    click.echo(click.style(f"  [{_ts()}] [INFO] {msg}", fg="green"))


def cmd(msg):
    click.echo(click.style(f"  [{_ts()}] [CMD]  {msg}", fg="yellow"))


def action(msg):
    click.echo(click.style(f"  [{_ts()}] [ACT]  {msg}", fg="blue"))


def skip(msg):
    click.echo(click.style(f"  [{_ts()}] [SKIP] {msg}", dim=True))


def error(msg):
    click.echo(click.style(f"  [{_ts()}] [FAIL] {msg}", fg="red", bold=True))
