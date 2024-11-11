# repo2llm

A simple tool to prepare repository contents for sharing with LLMs through your clipboard. Automatically formats your code files with proper file paths and supports multiple languages.

## Features

- 🚀 Simple command-line interface for easy usage
- 🔍 Content preview with customizable length
- 📋 Automatic clipboard integration
- 💻 Cross-platform support (Windows, macOS, Linux)
- ⚙️ Configuration file support (`.repo2llm`)
- 🧹 Built-in default ignore patterns for common files/directories

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
# Add custom ignore patterns
repo2llm . --ignore "*.log" --ignore "temp/*"

# Disable preview
repo2llm . --no-preview

# Customize preview length
repo2llm . --preview-length 300

# Use custom config file
repo2llm . --config my-config.txt
```

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


## Contributing

Contributions are welcome, feel free to submit a PR.

## License

MIT
