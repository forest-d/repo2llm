import subprocess
from pathlib import Path

import toml


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
    with open(pyproject_path, encoding='utf-8') as f:
        config = toml.load(f)
    return config['tool']['poetry']['version']


def bump_version(version_type: str) -> str:
    """
    Bump version based on semantic versioning.

    Args:
        version_type: One of 'major', 'minor', or 'patch'
    """
    current = get_current_version()
    major, minor, patch = map(int, current.split('.'))

    if version_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif version_type == 'minor':
        minor += 1
        patch = 0
    elif version_type == 'patch':
        patch += 1
    else:
        raise ValueError('Version type must be one of: major, minor, patch')

    new_version = f'{major}.{minor}.{patch}'
    return new_version


def update_version_in_pyproject(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
    with open(pyproject_path, encoding='utf-8') as f:
        config = toml.load(f)

    config['tool']['poetry']['version'] = new_version

    with open(pyproject_path, 'w', encoding='utf-8') as f:
        toml.dump(config, f)


def create_git_tag(version: str) -> None:
    """Create and push a git tag for the given version."""
    tag_name = f'v{version}'

    # Create tag
    subprocess.run(['git', 'tag', '-a', tag_name, '-m', f'Release {tag_name}'], check=True)

    # Push tag
    subprocess.run(['git', 'push', 'origin', tag_name], check=True)


def verify_git_clean() -> bool:
    """Verify that git working directory is clean."""
    status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
    return status.stdout.strip() == ''


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Manage semantic versioning')
    parser.add_argument('version_type', choices=['major', 'minor', 'patch'], help='Type of version bump to perform')
    parser.add_argument('--tag', action='store_true', help='Create and push a git tag for the new version')

    args = parser.parse_args()

    if not verify_git_clean():
        print('Error: Git working directory is not clean. Commit or stash changes first.')
        exit(1)

    try:
        new_version = bump_version(args.version_type)
        update_version_in_pyproject(new_version)
        print(f'Updated version to {new_version}')

        if args.tag:
            create_git_tag(new_version)
            print(f'Created and pushed tag v{new_version}')
    except Exception as e:
        print(f'Error: {e}')
        exit(1)
