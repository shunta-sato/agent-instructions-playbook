"""Outcome oracle for the local persistence journey; not a model-behavior grader."""
from pathlib import Path
import subprocess
import sys


def check(workspace: Path) -> None:
    def invoke(*args: str) -> str:
        result = subprocess.run(
            [sys.executable, str(workspace / 'app.py'), *args],
            cwd=workspace, capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0:
            raise AssertionError(f'{args}: exit {result.returncode}: {result.stderr}')
        return result.stdout

    if invoke('health') != 'ready\n':
        raise AssertionError('readiness did not produce the expected observable state')
    # Fresh subprocesses expose fake success and in-memory-only implementations.
    for value in ('evening', '  夜の設定  ', 'replacement'):
        if invoke('set', value) != 'saved\n':
            raise AssertionError('set failed')
        if invoke('get') != value + '\n':
            raise AssertionError('value did not persist across processes')
        if invoke('get') != value + '\n':
            raise AssertionError('read mutated or lost the saved value')


def main() -> int:
    try:
        check(Path(sys.argv[1]).resolve())
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print('Real CLI persistence boundary passed; ordering/communication review is separate.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
