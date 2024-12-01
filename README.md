# repo2llm

A simple tool to copy repository contents to your clipboard, useful for pasting into an LLM like Claude or ChatGPT.

## Installation

```bash
pip install repo2llm
```

## Usage

### Basic Usage
```bash
# Process current directory
repo2llm .

# Process specific directory
repo2llm /path/to/your/repo
```

### Advanced Options
```bash
# Add custom ignore patterns (supports wildcards)
repo2llm . --ignore "*.log"              # Ignore all .log files
repo2llm . --ignore "src/*.py"           # Ignore Python files in src directory
repo2llm . --ignore "**/test/**"         # Ignore anything in test directories
repo2llm . --ignore "build/**/*"         # Ignore all contents in build directory
repo2llm . --ignore "temp/"              # Ignore temp directory

# Multiple ignore patterns
repo2llm . --ignore "*.log" --ignore "temp/*" --ignore "**/test/*.py"

# Enable preview
repo2llm . --preview

# Customize preview length
repo2llm . --preview --preview-length 300

# Use custom config file
repo2llm . --config my-config.txt
```

The `--ignore` option supports glob-style patterns:
- `*` matches any characters except path separators
- `**` matches any characters including path separators (recursive)
- Patterns ending with `/` match directories
- Multiple patterns can be specified with multiple `--ignore` flags

## Configuration

### Default Ignore Patterns
The tool automatically ignores common development files and directories. See `repo2llm/constants.py` for the default list.

### Config File
You can create a `.repo2llm` file in your repository root to specify custom ignore patterns:

```text
# Development directories
.github/
.vscode/
node_modules/

# Build artifacts
dist/
build/
*.pyc

# Custom patterns
temp/
*.bak
```

The config file supports:
- One pattern per line
- Comments (lines starting with #)

## Development

### Tests

To run the test suite, run `poetry run pytest`

### Release

To release a new version, run the `scripts/version.py` script:

```bash
# For a patch update (0.1.0 -> 0.1.1)
poetry run python scripts/version.py patch --tag

# For a minor update (0.1.1 -> 0.2.0)
poetry run python scripts/version.py minor --tag

# For a major update (0.2.0 -> 1.0.0)
poetry run python scripts/version.py major --tag
```

### Contributing

Contributions are welcome, feel free to submit a PR.
