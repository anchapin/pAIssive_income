"""
Type stubs for os
"""
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, Iterator, AnyStr, overload, TypeVar, Generic

_T = TypeVar('_T')

# Constants
sep: str
altsep: Optional[str]
curdir: str
pardir: str
extsep: str
pathsep: str
linesep: str
defpath: str
name: str
devnull: str

# Functions
def getcwd() -> str: ...
def chdir(path: AnyStr) -> None: ...
def makedirs(name: AnyStr, mode: int = 0o777, exist_ok: bool = False) -> None: ...
def mkdir(path: AnyStr, mode: int = 0o777) -> None: ...
def remove(path: AnyStr) -> None: ...
def removedirs(name: AnyStr) -> None: ...
def rename(src: AnyStr, dst: AnyStr) -> None: ...
def renames(old: AnyStr, new: AnyStr) -> None: ...
def rmdir(path: AnyStr) -> None: ...
def stat(path: AnyStr) -> Any: ...
def stat_result(tuple: Tuple[int, ...]) -> Any: ...
def strerror(code: int) -> str: ...
def umask(mask: int) -> int: ...
def uname() -> Tuple[str, str, str, str, str]: ...
def unlink(path: AnyStr) -> None: ...
def utime(path: AnyStr, times: Optional[Tuple[float, float]] = None) -> None: ...
def walk(top: AnyStr, topdown: bool = True, onerror: Optional[Callable[[OSError], None]] = None, followlinks: bool = False) -> Iterator[Tuple[AnyStr, List[AnyStr], List[AnyStr]]]: ...

# Process management
def abort() -> None: ...
def execl(file: AnyStr, *args: AnyStr) -> None: ...
def execle(file: AnyStr, *args: Any) -> None: ...
def execlp(file: AnyStr, *args: AnyStr) -> None: ...
def execlpe(file: AnyStr, *args: Any) -> None: ...
def execv(path: AnyStr, args: List[AnyStr]) -> None: ...
def execve(path: AnyStr, args: List[AnyStr], env: Dict[str, str]) -> None: ...
def execvp(file: AnyStr, args: List[AnyStr]) -> None: ...
def execvpe(file: AnyStr, args: List[AnyStr], env: Dict[str, str]) -> None: ...
def _exit(n: int) -> None: ...
def fork() -> int: ...
def forkpty() -> Tuple[int, int]: ...
def kill(pid: int, sig: int) -> None: ...
def killpg(pgid: int, sig: int) -> None: ...
def nice(increment: int) -> int: ...
def plock(op: int) -> None: ...
def popen(cmd: AnyStr, mode: str = 'r', buffering: int = -1) -> Any: ...
def spawnl(mode: int, path: AnyStr, *args: AnyStr) -> int: ...
def spawnle(mode: int, path: AnyStr, *args: Any) -> int: ...
def spawnlp(mode: int, file: AnyStr, *args: AnyStr) -> int: ...
def spawnlpe(mode: int, file: AnyStr, *args: Any) -> int: ...
def spawnv(mode: int, path: AnyStr, args: List[AnyStr]) -> int: ...
def spawnve(mode: int, path: AnyStr, args: List[AnyStr], env: Dict[str, str]) -> int: ...
def spawnvp(mode: int, file: AnyStr, args: List[AnyStr]) -> int: ...
def spawnvpe(mode: int, file: AnyStr, args: List[AnyStr], env: Dict[str, str]) -> int: ...
def startfile(path: AnyStr, operation: Optional[str] = None) -> None: ...
def system(command: AnyStr) -> int: ...
def times() -> Tuple[float, float, float, float, float]: ...
def wait() -> Tuple[int, int]: ...
def waitpid(pid: int, options: int) -> Tuple[int, int]: ...
def wait3(options: int) -> Tuple[int, int, Any]: ...
def wait4(pid: int, options: int) -> Tuple[int, int, Any]: ...
def WCOREDUMP(status: int) -> bool: ...
def WIFCONTINUED(status: int) -> bool: ...
def WIFSTOPPED(status: int) -> bool: ...
def WIFSIGNALED(status: int) -> bool: ...
def WIFEXITED(status: int) -> bool: ...
def WEXITSTATUS(status: int) -> int: ...
def WSTOPSIG(status: int) -> int: ...
def WTERMSIG(status: int) -> int: ...

# Process groups
def getpgid(pid: int) -> int: ...
def getpgrp() -> int: ...
def getpid() -> int: ...
def getppid() -> int: ...
def setpgrp() -> int: ...
def setpgid(pid: int, pgrp: int) -> None: ...
def setsid() -> int: ...

# File descriptors
def close(fd: int) -> None: ...
def closerange(fd_low: int, fd_high: int) -> None: ...
def dup(fd: int) -> int: ...
def dup2(fd: int, fd2: int) -> None: ...
def fchmod(fd: int, mode: int) -> None: ...
def fchown(fd: int, uid: int, gid: int) -> None: ...
def fdatasync(fd: int) -> None: ...
def fpathconf(fd: int, name: str) -> int: ...
def fstat(fd: int) -> Any: ...
def fstatvfs(fd: int) -> Any: ...
def fsync(fd: int) -> None: ...
def ftruncate(fd: int, length: int) -> None: ...
def isatty(fd: int) -> bool: ...
def lseek(fd: int, pos: int, how: int) -> int: ...
def open(file: AnyStr, flags: int, mode: int = 0o777) -> int: ...
def openpty() -> Tuple[int, int]: ...
def pipe() -> Tuple[int, int]: ...
def read(fd: int, n: int) -> bytes: ...
def tcgetpgrp(fd: int) -> int: ...
def tcsetpgrp(fd: int, pg: int) -> None: ...
def ttyname(fd: int) -> str: ...
def write(fd: int, str: bytes) -> int: ...

# Special functions for Unix
def chroot(path: AnyStr) -> None: ...
def ctermid() -> str: ...
def getegid() -> int: ...
def geteuid() -> int: ...
def getgid() -> int: ...
def getgroups() -> List[int]: ...
def getlogin() -> str: ...
def getresgid() -> Tuple[int, int, int]: ...
def getresuid() -> Tuple[int, int, int]: ...
def getuid() -> int: ...
def initgroups(username: str, gid: int) -> None: ...
def setegid(egid: int) -> None: ...
def seteuid(euid: int) -> None: ...
def setgid(gid: int) -> None: ...
def setgroups(groups: List[int]) -> None: ...
def setregid(rgid: int, egid: int) -> None: ...
def setresgid(rgid: int, egid: int, sgid: int) -> None: ...
def setresuid(ruid: int, euid: int, suid: int) -> None: ...
def setreuid(ruid: int, euid: int) -> None: ...
def setuid(uid: int) -> None: ...

# Process control
def setsid() -> None: ...
def getpgid(pid: int) -> int: ...
def getpgrp() -> int: ...
def setpgrp() -> None: ...
def setpgid(pid: int, pgrp: int) -> None: ...
def killpg(pgid: int, sig: int) -> None: ...
def getpgid(pid: int) -> int: ...
def setsid() -> int: ...

# Path manipulation
def access(path: AnyStr, mode: int) -> bool: ...
def chdir(path: AnyStr) -> None: ...
def fchdir(fd: int) -> None: ...
def getcwd() -> str: ...
def getcwdb() -> bytes: ...
def chflags(path: AnyStr, flags: int) -> None: ...
def chroot(path: AnyStr) -> None: ...
def chmod(path: AnyStr, mode: int) -> None: ...
def chown(path: AnyStr, uid: int, gid: int) -> None: ...
def lchflags(path: AnyStr, flags: int) -> None: ...
def lchmod(path: AnyStr, mode: int) -> None: ...
def lchown(path: AnyStr, uid: int, gid: int) -> None: ...
def link(src: AnyStr, dst: AnyStr) -> None: ...
def listdir(path: AnyStr) -> List[AnyStr]: ...
def lstat(path: AnyStr) -> Any: ...
def mkfifo(path: AnyStr, mode: int = 0o666) -> None: ...
def mknod(path: AnyStr, mode: int = 0o600, device: int = 0) -> None: ...
def major(device: int) -> int: ...
def minor(device: int) -> int: ...
def makedev(major: int, minor: int) -> int: ...
def mkdir(path: AnyStr, mode: int = 0o777) -> None: ...
def makedirs(path: AnyStr, mode: int = 0o777, exist_ok: bool = False) -> None: ...
def pathconf(path: AnyStr, name: str) -> int: ...
def readlink(path: AnyStr) -> AnyStr: ...
def remove(path: AnyStr) -> None: ...
def removedirs(path: AnyStr) -> None: ...
def rename(src: AnyStr, dst: AnyStr) -> None: ...
def renames(old: AnyStr, new: AnyStr) -> None: ...
def rmdir(path: AnyStr) -> None: ...
def stat(path: AnyStr) -> Any: ...
def stat_float_times(newvalue: Optional[bool] = None) -> bool: ...
def statvfs(path: AnyStr) -> Any: ...
def symlink(src: AnyStr, dst: AnyStr, target_is_directory: bool = False) -> None: ...
def unlink(path: AnyStr) -> None: ...
def utime(path: AnyStr, times: Optional[Tuple[float, float]] = None) -> None: ...
def walk(top: AnyStr, topdown: bool = True, onerror: Optional[Callable[[OSError], None]] = None, followlinks: bool = False) -> Iterator[Tuple[AnyStr, List[AnyStr], List[AnyStr]]]: ...

# Environment variables
def getenv(key: str, default: Optional[str] = None) -> Optional[str]: ...
def putenv(key: str, value: str) -> None: ...
def unsetenv(key: str) -> None: ...
def environ() -> Dict[str, str]: ...

# Special functions for Windows
def startfile(path: AnyStr, operation: Optional[str] = None) -> None: ...
def system(command: AnyStr) -> int: ...

# Additional functions
def urandom(n: int) -> bytes: ...
def get_terminal_size() -> Tuple[int, int]: ...
def cpu_count() -> Optional[int]: ...
def get_inheritable(fd: int) -> bool: ...
def set_inheritable(fd: int, inheritable: bool) -> None: ...
def get_blocking(fd: int) -> bool: ...
def set_blocking(fd: int, blocking: bool) -> None: ...
def scandir(path: AnyStr) -> Iterator[Any]: ...
def fspath(path: Union[str, bytes, 'PathLike']) -> Union[str, bytes]: ...
class PathLike:
    def __fspath__(self) -> str: ...

class path:
    abspath: Callable[[AnyStr], AnyStr]
    basename: Callable[[AnyStr], AnyStr]
    commonpath: Callable[[List[AnyStr]], AnyStr]
    commonprefix: Callable[[List[AnyStr]], AnyStr]
    dirname: Callable[[AnyStr], AnyStr]
    exists: Callable[[AnyStr], bool]
    expanduser: Callable[[AnyStr], AnyStr]
    expandvars: Callable[[AnyStr], AnyStr]
    getatime: Callable[[AnyStr], float]
    getctime: Callable[[AnyStr], float]
    getmtime: Callable[[AnyStr], float]
    getsize: Callable[[AnyStr], int]
    isabs: Callable[[AnyStr], bool]
    isdir: Callable[[AnyStr], bool]
    isfile: Callable[[AnyStr], bool]
    islink: Callable[[AnyStr], bool]
    ismount: Callable[[AnyStr], bool]
    join: Callable[..., AnyStr]
    lexists: Callable[[AnyStr], bool]
    normcase: Callable[[AnyStr], AnyStr]
    normpath: Callable[[AnyStr], AnyStr]
    realpath: Callable[[AnyStr], AnyStr]
    relpath: Callable[[AnyStr, Optional[AnyStr]], AnyStr]
    samefile: Callable[[AnyStr, AnyStr], bool]
    sameopenfile: Callable[[int, int], bool]
    samestat: Callable[[Any, Any], bool]
    split: Callable[[AnyStr], Tuple[AnyStr, AnyStr]]
    splitdrive: Callable[[AnyStr], Tuple[AnyStr, AnyStr]]
    splitext: Callable[[AnyStr], Tuple[AnyStr, AnyStr]]
