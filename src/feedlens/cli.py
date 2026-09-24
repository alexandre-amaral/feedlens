"""CLI scaffold (task T-0.7)."""

from __future__ import annotations

import typer

app = typer.Typer(help="feedlens — your feed, your algorithm.")


@app.command()
def init() -> None:
    """Create ~/.feedlens and the database."""
    raise typer.Exit(code=_todo("T-0.7"))


@app.command()
def serve() -> None:
    """Run the API + UI."""
    raise typer.Exit(code=_todo("T-2.12"))


@app.command()
def refresh() -> None:
    """Pull → embed → decide → rank."""
    raise typer.Exit(code=_todo("T-2.10"))


def _todo(task: str) -> int:
    typer.echo(f"Not implemented yet — see tasks/mvp-tasks.md ({task})")
    return 2


if __name__ == "__main__":
    app()
