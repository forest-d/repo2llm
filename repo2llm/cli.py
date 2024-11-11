from pathlib import Path

import click
import pyperclip
from rich.console import Console
from rich.panel import Panel

from repo2llm.config import find_config_file, load_config_file
from repo2llm.core import RepoConfig, RepoProcessor

console = Console()


@click.command()
@click.argument(
    'directory',
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
)
@click.option(
    '--ignore',
    '-i',
    multiple=True,
    help='Additional patterns to ignore (e.g., "*.txt", "temp/")',
)
@click.option('--preview/--no-preview', default=True, help='Show preview of copied content')
@click.option('--preview-length', default=200, help='Length of preview in characters')
@click.option(
    '--config',
    '-c',
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help='Path to config file (defaults to .repo2llm in repository root)',
)
def main(
    directory: Path,
    ignore: list[str],
    preview: bool,
    preview_length: int,
    config: Path | None,
) -> None:
    """
    Copy repository contents to clipboard for sharing with LLMs.

    DIRECTORY is the root directory to process (defaults to current directory)
    """
    try:
        # Create config with base ignore patterns
        repo_config = RepoConfig(root_dir=directory)

        # First try explicit config file
        config_settings = None
        if config:
            try:
                config_settings = load_config_file(config)
                console.print(f'[green]Using config file: {config}[/green]')
            except Exception as e:
                console.print(f'[yellow]Warning: Error loading config file {config}: {e}[/yellow]')

        # If no explicit config, try to find .repo2llm file
        elif config_file := find_config_file(directory):
            try:
                config_settings = load_config_file(config_file)
                console.print(f'[green]Using config file: {config_file}[/green]')
            except Exception as e:
                console.print(f'[yellow]Warning: Error loading config file {config_file}: {e}[/yellow]')

        # Apply config file patterns if they exist
        if config_settings and config_settings.ignore:
            repo_config.add_ignore_patterns(config_settings.ignore)

        # Add CLI ignore patterns (these take precedence over config file)
        if ignore:
            repo_config.add_ignore_patterns(set(ignore))

        # Process repository
        processor = RepoProcessor(repo_config)
        output, file_count = processor.process_repository()

        # Copy to clipboard
        pyperclip.copy(output)

        # Show success message
        console.print(Panel.fit(f'✨ {file_count} files copied to clipboard! ✨', style='green'))

        # Show preview if enabled
        if preview and output:
            preview_text = output[:preview_length]
            if len(output) > preview_length:
                preview_text += '...'

            console.print('\n[bold]Preview of copied content:[/bold]')
            console.print(Panel(preview_text, style='blue'))

    except Exception as e:
        console.print(f'[red]Error: {e!s}[/red]')
        raise click.Abort() from e


if __name__ == '__main__':
    main()
