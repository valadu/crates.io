__all__ = ['Git']


import pathlib as p
import subprocess


class Git:
    '''
    Example:
        >>> Git(cwd='.', assertion=True) \
        ...     .add(...) \
        ...     .commit(...) \
        ...     .push() \
        ...     .gc()
    '''

    def __init__(self, cwd: str = '.', assertion: bool = False) -> None:
        self._cwd = p.Path(cwd)
        self._cwd.mkdir(parents=True, exist_ok=True)
        self._assertion = assertion

    def init(self) -> 'Git':
        if not (self._cwd/'.git').exists():
            self._git('init')
        return self

    def add(self, *args: str) -> 'Git':
        return self._api('add', *args)

    def commit(self, message: str) -> 'Git':
        return self._api('commit', '-m', message)

    def push(self) -> 'Git':
        return self._api('push')

    def gc(self) -> 'Git':
        return self._api('gc')

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(list(map(str, args)), capture_output=True, cwd=self._cwd)

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        cp = self._run('git', *args)
        if self._assertion:
            assert not cp.returncode, cp.stderr.decode()
        return cp

    def _api(self, *args) -> 'Git':
        self._git(*args)
        return self
