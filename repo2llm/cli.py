from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.panel import Panel

import pyperclip

from .core import RepoConfig, RepoProcessor

console = Console()


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True,
                                             path_type=Path), default=Path.cwd())
@click.option('--ignore', '-i', multiple=True,
              help='Additional patterns to ignore (e.g., "*.txt", "temp/")')
@click.option('--include', '-n', multiple=True,
              help='Only include files matching these patterns (e.g., "*.py", "src/*.ts")')
@click.option('--preview/--no-preview', default=True,
              help='Show preview of copied content')
@click.option('--preview-length', default=200,
              help='Length of preview in characters')
def main(directory: Path,
         ignore: List[str],
         include: List[str],
         preview: bool,
         preview_length: int) -> None:
    """
    Copy repository contents to clipboard for sharing with LLMs.

    DIRECTORY is the root directory to process (defaults to current directory)
    """
    try:
        # Create config with base ignore patterns and add user-specified ones
        config = RepoConfig(root_dir=directory)
        if ignore:
            config.add_ignore_patterns(set(ignore))

        if include:
            config.include_patterns = set(include)

        # Process repository
        processor = RepoProcessor(config)
        output = processor.process_repository()

        # Copy to clipboard
        pyperclip.copy(output)

        # Show success message
        console.print(Panel.fit(
            "✨ Repository contents copied to clipboard! ✨",
            style="green"
        ))

        # Show preview if enabled
        if preview and output:
            preview_text = output[:preview_length]
            if len(output) > preview_length:
                preview_text += "..."

            console.print("\n[bold]Preview of copied content:[/bold]")
            console.print(Panel(preview_text, style="blue"))

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()


if __name__ == '__main__':
    main()