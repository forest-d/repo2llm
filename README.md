# repo2llm

A simple tool to prepare repository contents for sharing with LLMs through your clipboard. Automatically formats your code files with proper file paths and supports multiple languages.

## Installation

```bash
pip install repo2llm
```

## Usage

Basic usage (from current directory):
```bash
repo2llm .
```

Specify directory:
```bash
repo2llm /path/to/your/repo
```

With custom ignore patterns:
```bash
repo2llm . --ignore "*.log" --ignore "temp/*"
```

Only include specific files:
```bash
repo2llm . --include "*.py" --include "src/*.ts"
```

Disable preview:
```bash
repo2llm . --no-preview
```

## Features

- 🚀 Easy to use CLI interface
- 📁 Support for Python, JavaScript, and TypeScript files
- 🎯 Customizable ignore patterns
- 🎨 Language-specific formatting
- 📋 Automatic clipboard copy
- 💻 Cross-platform support (Windows, macOS, Linux)
- 🔍 Preview support
- ⚡ Fast and efficient processing

## Extending

To add support for new file types, subclass `BaseFormatter` and add the extension to `FORMATTERS` in `formatters/__init__.py`.

## Contributing

Contributions are welcome, feel free to submit a PR.

## License

MIT
