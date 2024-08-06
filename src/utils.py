from pathlib import Path


def is_ran_by_pytest() -> None:
    """Check that this code ran from pytest.

    Try to avoid using this function!
    :returns: None, but raises if this code not ran from pytest.
    """
    import sys

    if 'pytest' not in sys.modules:
        msg = (
            'You are trying to run this project not from root directory. This '
            'will broke some paths, so running from other directories not '
            'allowed. Please run project from root directory.'
        )
        raise RuntimeError(msg)


def get_root() -> str:
    """Get path to root if run test from subdirectories.

    :returns: parent path.
    """
    match Path.cwd().name:
        case 'src':
            return '../'
        case 'tests':
            return '../../'
        case 'auto':
            return '../../../'
        # means root directory
        case _:
            return ''


def correct_path(initial: str) -> str:
    """Get path for testing.

    You could run tests from different places: project root, "tests"
    directory (that could do PyCharm for example), "src" or "auto" (why
    not?). Depends on it, paths must be different to pass path validation.
    :param str initial: path.
    :returns: dict with paths.
    """
    parent = get_root()
    return f'{parent}{initial}'


def correct_paths(initial: dict[str, str]) -> dict[str, str]:
    """Get paths for testing.

    You could run tests from different places: project root, "tests"
    directory (that could do PyCharm for example), "src" or "auto" (why
    not?). Depends on it, paths must be different to pass path validation.
    :param dict[str, str] initial: dict with paths.
    :returns: dict with paths.
    """
    parent = get_root()
    return {
        name: path if Path(path).is_absolute() else f'{parent}{path}'
        for name, path in initial.items()
    }
