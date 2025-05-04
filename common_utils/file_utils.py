"""
"""
File utilities for the pAIssive Income project.
File utilities for the pAIssive Income project.


This module provides common file handling functions used across the project.
This module provides common file handling functions used across the project.
"""
"""




import asyncio
import asyncio
import logging
import logging
import os
import os
import shutil
import shutil
from typing import Any, List, Optional, Union
from typing import Any, List, Optional, Union


from ai_models.async_utils import run_in_thread
from ai_models.async_utils import run_in_thread


# Import the run_in_thread utility for async operations
# Import the run_in_thread utility for async operations
# Set up logging
# Set up logging
logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)


# Async file operation lock for concurrent access control
# Async file operation lock for concurrent access control
_file_lock = asyncio.Lock()
_file_lock = asyncio.Lock()




def read_file(
def read_file(
file_path: str, binary: bool = False, encoding: str = "utf-8"
file_path: str, binary: bool = False, encoding: str = "utf-8"
) -> Union[str, bytes]:
    ) -> Union[str, bytes]:
    """
    """
    Read content from a file.
    Read content from a file.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file
    binary: Whether to read in binary mode (default: False)
    binary: Whether to read in binary mode (default: False)
    encoding: Encoding to use when reading text (default: utf-8)
    encoding: Encoding to use when reading text (default: utf-8)


    Returns:
    Returns:
    File content as string or bytes
    File content as string or bytes


    Raises:
    Raises:
    FileNotFoundError: If the file doesn't exist
    FileNotFoundError: If the file doesn't exist
    IOError: If there's an issue reading the file
    IOError: If there's an issue reading the file
    """
    """
    try:
    try:
    mode = "rb" if binary else "r"
    mode = "rb" if binary else "r"
    kwargs = {} if binary else {"encoding": encoding}
    kwargs = {} if binary else {"encoding": encoding}


    with open(file_path, mode, **kwargs) as f:  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error
    with open(file_path, mode, **kwargs) as f:  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error  # FIXME: Syntax error
    content = f.read()
    content = f.read()


    logger.debug(f"Successfully read file: {file_path}")
    logger.debug(f"Successfully read file: {file_path}")
    return content
    return content
except FileNotFoundError:
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    logger.error(f"File not found: {file_path}")
    raise
    raise
except (IOError, OSError) as e:
except (IOError, OSError) as e:
    logger.error(f"Error reading file {file_path}: {e}")
    logger.error(f"Error reading file {file_path}: {e}")
    raise
    raise




    def write_file(
    def write_file(
    file_path: str,
    file_path: str,
    content: Union[str, bytes],
    content: Union[str, bytes],
    binary: bool = False,
    binary: bool = False,
    encoding: str = "utf-8",
    encoding: str = "utf-8",
    create_dirs: bool = True,
    create_dirs: bool = True,
    ) -> None:
    ) -> None:
    """
    """
    Write content to a file.
    Write content to a file.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file
    content: Content to write
    content: Content to write
    binary: Whether to write in binary mode (default: False)
    binary: Whether to write in binary mode (default: False)
    encoding: Encoding to use when writing text (default: utf-8)
    encoding: Encoding to use when writing text (default: utf-8)
    create_dirs: Whether to create parent directories if they don't exist (default: True)
    create_dirs: Whether to create parent directories if they don't exist (default: True)


    Raises:
    Raises:
    IOError: If there's an issue writing to the file
    IOError: If there's an issue writing to the file
    """
    """
    try:
    try:
    # Create parent directories if they don't exist
    # Create parent directories if they don't exist
    if create_dirs:
    if create_dirs:
    directory = os.path.dirname(file_path)
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
    if directory and not os.path.exists(directory):
    os.makedirs(directory, exist_ok=True)
    os.makedirs(directory, exist_ok=True)


    mode = "wb" if binary else "w"
    mode = "wb" if binary else "w"
    kwargs = {} if binary else {"encoding": encoding}
    kwargs = {} if binary else {"encoding": encoding}


    with open(file_path, mode, **kwargs) as f:
    with open(file_path, mode, **kwargs) as f:
    f.write(content)
    f.write(content)


    logger.debug(f"Successfully wrote to file: {file_path}")
    logger.debug(f"Successfully wrote to file: {file_path}")
except (IOError, OSError) as e:
except (IOError, OSError) as e:
    logger.error(f"Error writing to file {file_path}: {e}")
    logger.error(f"Error writing to file {file_path}: {e}")
    raise
    raise




    def file_exists(file_path: str) -> bool:
    def file_exists(file_path: str) -> bool:
    """
    """
    Check if a file exists.
    Check if a file exists.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    True if the file exists, False otherwise
    True if the file exists, False otherwise
    """
    """
    return os.path.isfile(file_path)
    return os.path.isfile(file_path)




    def create_directory(directory_path: str, exist_ok: bool = True) -> None:
    def create_directory(directory_path: str, exist_ok: bool = True) -> None:
    """
    """
    Create a directory.
    Create a directory.


    Args:
    Args:
    directory_path: Path to the directory
    directory_path: Path to the directory
    exist_ok: Whether to ignore if the directory already exists (default: True)
    exist_ok: Whether to ignore if the directory already exists (default: True)


    Raises:
    Raises:
    OSError: If there's an issue creating the directory
    OSError: If there's an issue creating the directory
    """
    """
    try:
    try:
    os.makedirs(directory_path, exist_ok=exist_ok)
    os.makedirs(directory_path, exist_ok=exist_ok)
    logger.debug(f"Successfully created directory: {directory_path}")
    logger.debug(f"Successfully created directory: {directory_path}")
except OSError as e:
except OSError as e:
    logger.error(f"Error creating directory {directory_path}: {e}")
    logger.error(f"Error creating directory {directory_path}: {e}")
    raise
    raise




    def get_file_path(directory: str, filename: str) -> str:
    def get_file_path(directory: str, filename: str) -> str:
    """
    """
    Get the full path to a file.
    Get the full path to a file.


    Args:
    Args:
    directory: Directory path
    directory: Directory path
    filename: File name
    filename: File name


    Returns:
    Returns:
    Full path to the file
    Full path to the file
    """
    """
    return os.path.join(directory, filename)
    return os.path.join(directory, filename)




    def get_directory_path(base_dir: str, *subdirs: str) -> str:
    def get_directory_path(base_dir: str, *subdirs: str) -> str:
    """
    """
    Get the full path to a directory.
    Get the full path to a directory.


    Args:
    Args:
    base_dir: Base directory path
    base_dir: Base directory path
    *subdirs: Subdirectories
    *subdirs: Subdirectories


    Returns:
    Returns:
    Full path to the directory
    Full path to the directory
    """
    """
    return os.path.join(base_dir, *subdirs)
    return os.path.join(base_dir, *subdirs)




    def list_files(
    def list_files(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    List files in a directory.
    List files in a directory.


    Args:
    Args:
    directory: Directory path
    directory: Directory path
    pattern: File pattern to match (default: None)
    pattern: File pattern to match (default: None)
    recursive: Whether to search recursively (default: False)
    recursive: Whether to search recursively (default: False)


    Returns:
    Returns:
    List of file paths
    List of file paths


    Raises:
    Raises:
    FileNotFoundError: If the directory doesn't exist
    FileNotFoundError: If the directory doesn't exist
    """
    """
    try:
    try:
    if not os.path.isdir(directory):
    if not os.path.isdir(directory):
    raise FileNotFoundError(f"Directory not found: {directory}")
    raise FileNotFoundError(f"Directory not found: {directory}")


    files = []
    files = []


    if recursive:
    if recursive:
    for root, _, filenames in os.walk(directory):
    for root, _, filenames in os.walk(directory):
    for filename in filenames:
    for filename in filenames:
    if pattern is None or pattern in filename:
    if pattern is None or pattern in filename:
    files.append(os.path.join(root, filename))
    files.append(os.path.join(root, filename))
    else:
    else:
    for filename in os.listdir(directory):
    for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path) and (
    if os.path.isfile(file_path) and (
    pattern is None or pattern in filename
    pattern is None or pattern in filename
    ):
    ):
    files.append(file_path)
    files.append(file_path)


    return files
    return files
except (FileNotFoundError, OSError) as e:
except (FileNotFoundError, OSError) as e:
    logger.error(f"Error listing files in {directory}: {e}")
    logger.error(f"Error listing files in {directory}: {e}")
    raise
    raise




    def list_directories(
    def list_directories(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    List subdirectories in a directory.
    List subdirectories in a directory.


    Args:
    Args:
    directory: Directory path
    directory: Directory path
    pattern: Directory pattern to match (default: None)
    pattern: Directory pattern to match (default: None)
    recursive: Whether to search recursively (default: False)
    recursive: Whether to search recursively (default: False)


    Returns:
    Returns:
    List of directory paths
    List of directory paths


    Raises:
    Raises:
    FileNotFoundError: If the directory doesn't exist
    FileNotFoundError: If the directory doesn't exist
    """
    """
    try:
    try:
    if not os.path.isdir(directory):
    if not os.path.isdir(directory):
    raise FileNotFoundError(f"Directory not found: {directory}")
    raise FileNotFoundError(f"Directory not found: {directory}")


    directories = []
    directories = []


    if recursive:
    if recursive:
    for root, dirs, _ in os.walk(directory):
    for root, dirs, _ in os.walk(directory):
    for dir_name in dirs:
    for dir_name in dirs:
    if pattern is None or pattern in dir_name:
    if pattern is None or pattern in dir_name:
    directories.append(os.path.join(root, dir_name))
    directories.append(os.path.join(root, dir_name))
    else:
    else:
    for dir_name in os.listdir(directory):
    for dir_name in os.listdir(directory):
    dir_path = os.path.join(directory, dir_name)
    dir_path = os.path.join(directory, dir_name)
    if os.path.isdir(dir_path) and (pattern is None or pattern in dir_name):
    if os.path.isdir(dir_path) and (pattern is None or pattern in dir_name):
    directories.append(dir_path)
    directories.append(dir_path)


    return directories
    return directories
except (FileNotFoundError, OSError) as e:
except (FileNotFoundError, OSError) as e:
    logger.error(f"Error listing directories in {directory}: {e}")
    logger.error(f"Error listing directories in {directory}: {e}")
    raise
    raise




    def get_file_extension(file_path: str) -> str:
    def get_file_extension(file_path: str) -> str:
    """
    """
    Get the extension of a file.
    Get the extension of a file.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    File extension (without the dot)
    File extension (without the dot)
    """
    """
    return os.path.splitext(file_path)[1][1:]
    return os.path.splitext(file_path)[1][1:]




    def get_file_name(file_path: str, with_extension: bool = True) -> str:
    def get_file_name(file_path: str, with_extension: bool = True) -> str:
    """
    """
    Get the name of a file.
    Get the name of a file.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file
    with_extension: Whether to include the extension (default: True)
    with_extension: Whether to include the extension (default: True)


    Returns:
    Returns:
    File name
    File name
    """
    """
    if with_extension:
    if with_extension:
    return os.path.basename(file_path)
    return os.path.basename(file_path)
    return os.path.splitext(os.path.basename(file_path))[0]
    return os.path.splitext(os.path.basename(file_path))[0]




    def get_file_size(file_path: str) -> int:
    def get_file_size(file_path: str) -> int:
    """
    """
    Get the size of a file in bytes.
    Get the size of a file in bytes.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    File size in bytes
    File size in bytes


    Raises:
    Raises:
    FileNotFoundError: If the file doesn't exist
    FileNotFoundError: If the file doesn't exist
    """
    """
    try:
    try:
    return os.path.getsize(file_path)
    return os.path.getsize(file_path)
except (FileNotFoundError, OSError) as e:
except (FileNotFoundError, OSError) as e:
    logger.error(f"Error getting size of file {file_path}: {e}")
    logger.error(f"Error getting size of file {file_path}: {e}")
    raise
    raise




    async def read_file_async(
    async def read_file_async(
    file_path: str, binary: bool = False, encoding: str = "utf-8"
    file_path: str, binary: bool = False, encoding: str = "utf-8"
    ) -> Union[str, bytes]:
    ) -> Union[str, bytes]:
    """
    """
    Read content from a file asynchronously.
    Read content from a file asynchronously.


    This is the asynchronous version of read_file() that doesn't block the
    This is the asynchronous version of read_file() that doesn't block the
    main event loop during file I/O operations.
    main event loop during file I/O operations.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file
    binary: Whether to read in binary mode (default: False)
    binary: Whether to read in binary mode (default: False)
    encoding: Encoding to use when reading text (default: utf-8)
    encoding: Encoding to use when reading text (default: utf-8)


    Returns:
    Returns:
    File content as string or bytes
    File content as string or bytes


    Raises:
    Raises:
    FileNotFoundError: If the file doesn't exist
    FileNotFoundError: If the file doesn't exist
    IOError: If there's an issue reading the file
    IOError: If there's an issue reading the file
    """
    """
    # Use run_in_thread to run the blocking I/O operation in a thread pool
    # Use run_in_thread to run the blocking I/O operation in a thread pool
    try:
    try:
    async with _file_lock:
    async with _file_lock:
    return await run_in_thread(read_file, file_path, binary, encoding)
    return await run_in_thread(read_file, file_path, binary, encoding)
except Exception as e:
except Exception as e:
    logger.error(f"Error in read_file_async for {file_path}: {e}")
    logger.error(f"Error in read_file_async for {file_path}: {e}")
    raise
    raise




    async def write_file_async(
    async def write_file_async(
    file_path: str,
    file_path: str,
    content: Union[str, bytes],
    content: Union[str, bytes],
    binary: bool = False,
    binary: bool = False,
    encoding: str = "utf-8",
    encoding: str = "utf-8",
    create_dirs: bool = True,
    create_dirs: bool = True,
    ) -> None:
    ) -> None:
    """
    """
    Write content to a file asynchronously.
    Write content to a file asynchronously.


    This is the asynchronous version of write_file() that doesn't block the
    This is the asynchronous version of write_file() that doesn't block the
    main event loop during file I/O operations.
    main event loop during file I/O operations.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file
    content: Content to write
    content: Content to write
    binary: Whether to write in binary mode (default: False)
    binary: Whether to write in binary mode (default: False)
    encoding: Encoding to use when writing text (default: utf-8)
    encoding: Encoding to use when writing text (default: utf-8)
    create_dirs: Whether to create parent directories if they don't exist (default: True)
    create_dirs: Whether to create parent directories if they don't exist (default: True)


    Raises:
    Raises:
    IOError: If there's an issue writing to the file
    IOError: If there's an issue writing to the file
    """
    """
    try:
    try:
    async with _file_lock:
    async with _file_lock:
    await run_in_thread(
    await run_in_thread(
    write_file, file_path, content, binary, encoding, create_dirs
    write_file, file_path, content, binary, encoding, create_dirs
    )
    )
    logger.debug(f"Successfully wrote to file asynchronously: {file_path}")
    logger.debug(f"Successfully wrote to file asynchronously: {file_path}")
except Exception as e:
except Exception as e:
    logger.error(f"Error in write_file_async for {file_path}: {e}")
    logger.error(f"Error in write_file_async for {file_path}: {e}")
    raise
    raise




    async def file_exists_async(file_path: str) -> bool:
    async def file_exists_async(file_path: str) -> bool:
    """
    """
    Check if a file exists asynchronously.
    Check if a file exists asynchronously.


    This is the asynchronous version of file_exists() that doesn't block the
    This is the asynchronous version of file_exists() that doesn't block the
    main event loop during file I/O operations.
    main event loop during file I/O operations.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    True if the file exists, False otherwise
    True if the file exists, False otherwise
    """
    """
    return await run_in_thread(os.path.isfile, file_path)
    return await run_in_thread(os.path.isfile, file_path)




    async def create_directory_async(directory_path: str, exist_ok: bool = True) -> None:
    async def create_directory_async(directory_path: str, exist_ok: bool = True) -> None:
    """
    """
    Create a directory asynchronously.
    Create a directory asynchronously.


    This is the asynchronous version of create_directory() that doesn't block the
    This is the asynchronous version of create_directory() that doesn't block the
    main event loop during file I/O operations.
    main event loop during file I/O operations.


    Args:
    Args:
    directory_path: Path to the directory
    directory_path: Path to the directory
    exist_ok: Whether to ignore if the directory already exists (default: True)
    exist_ok: Whether to ignore if the directory already exists (default: True)


    Raises:
    Raises:
    OSError: If there's an issue creating the directory
    OSError: If there's an issue creating the directory
    """
    """
    try:
    try:
    await run_in_thread(create_directory, directory_path, exist_ok)
    await run_in_thread(create_directory, directory_path, exist_ok)
    logger.debug(f"Successfully created directory asynchronously: {directory_path}")
    logger.debug(f"Successfully created directory asynchronously: {directory_path}")
except Exception as e:
except Exception as e:
    logger.error(f"Error in create_directory_async for {directory_path}: {e}")
    logger.error(f"Error in create_directory_async for {directory_path}: {e}")
    raise
    raise




    async def list_files_async(
    async def list_files_async(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    List files in a directory asynchronously.
    List files in a directory asynchronously.


    This is the asynchronous version of list_files() that doesn't block the
    This is the asynchronous version of list_files() that doesn't block the
    main event loop during file I/O operations, which is particularly beneficial
    main event loop during file I/O operations, which is particularly beneficial
    for large directories or network file systems.
    for large directories or network file systems.


    Args:
    Args:
    directory: Directory path
    directory: Directory path
    pattern: File pattern to match (default: None)
    pattern: File pattern to match (default: None)
    recursive: Whether to search recursively (default: False)
    recursive: Whether to search recursively (default: False)


    Returns:
    Returns:
    List of file paths
    List of file paths


    Raises:
    Raises:
    FileNotFoundError: If the directory doesn't exist
    FileNotFoundError: If the directory doesn't exist
    """
    """
    return await run_in_thread(list_files, directory, pattern, recursive)
    return await run_in_thread(list_files, directory, pattern, recursive)




    async def list_directories_async(
    async def list_directories_async(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    directory: str, pattern: Optional[str] = None, recursive: bool = False
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    List subdirectories in a directory asynchronously.
    List subdirectories in a directory asynchronously.


    This is the asynchronous version of list_directories() that doesn't block the
    This is the asynchronous version of list_directories() that doesn't block the
    main event loop during file I/O operations, which is particularly beneficial
    main event loop during file I/O operations, which is particularly beneficial
    for large directories or network file systems.
    for large directories or network file systems.


    Args:
    Args:
    directory: Directory path
    directory: Directory path
    pattern: Directory pattern to match (default: None)
    pattern: Directory pattern to match (default: None)
    recursive: Whether to search recursively (default: False)
    recursive: Whether to search recursively (default: False)


    Returns:
    Returns:
    List of directory paths
    List of directory paths


    Raises:
    Raises:
    FileNotFoundError: If the directory doesn't exist
    FileNotFoundError: If the directory doesn't exist
    """
    """
    return await run_in_thread(list_directories, directory, pattern, recursive)
    return await run_in_thread(list_directories, directory, pattern, recursive)




    async def get_file_size_async(file_path: str) -> int:
    async def get_file_size_async(file_path: str) -> int:
    """
    """
    Get the size of a file in bytes asynchronously.
    Get the size of a file in bytes asynchronously.


    This is the asynchronous version of get_file_size() that doesn't block the
    This is the asynchronous version of get_file_size() that doesn't block the
    main event loop during file I/O operations.
    main event loop during file I/O operations.


    Args:
    Args:
    file_path: Path to the file
    file_path: Path to the file


    Returns:
    Returns:
    File size in bytes
    File size in bytes


    Raises:
    Raises:
    FileNotFoundError: If the file doesn't exist
    FileNotFoundError: If the file doesn't exist
    """
    """
    return await run_in_thread(get_file_size, file_path)
    return await run_in_thread(get_file_size, file_path)




    async def copy_file_async(
    async def copy_file_async(
    src_path: str, dest_path: str, overwrite: bool = False
    src_path: str, dest_path: str, overwrite: bool = False
    ) -> None:
    ) -> None:
    """
    """
    Copy a file asynchronously.
    Copy a file asynchronously.


    Args:
    Args:
    src_path: Path to the source file
    src_path: Path to the source file
    dest_path: Path where the file should be copied
    dest_path: Path where the file should be copied
    overwrite: Whether to overwrite the destination file if it exists
    overwrite: Whether to overwrite the destination file if it exists


    Raises:
    Raises:
    FileNotFoundError: If the source file doesn't exist
    FileNotFoundError: If the source file doesn't exist
    IOError: If there's an issue copying the file
    IOError: If there's an issue copying the file
    """
    """
    try:
    try:
    if not overwrite and await file_exists_async(dest_path):
    if not overwrite and await file_exists_async(dest_path):
    raise FileExistsError(f"Destination file already exists: {dest_path}")
    raise FileExistsError(f"Destination file already exists: {dest_path}")


    async with _file_lock:
    async with _file_lock:
    await run_in_thread(shutil.copy2, src_path, dest_path)
    await run_in_thread(shutil.copy2, src_path, dest_path)


    logger.debug(
    logger.debug(
    f"Successfully copied file asynchronously: {src_path} -> {dest_path}"
    f"Successfully copied file asynchronously: {src_path} -> {dest_path}"
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error in copy_file_async: {e}")
    logger.error(f"Error in copy_file_async: {e}")
    raise
    raise




    async def move_file_async(
    async def move_file_async(
    src_path: str, dest_path: str, overwrite: bool = False
    src_path: str, dest_path: str, overwrite: bool = False
    ) -> None:
    ) -> None:
    """
    """
    Move a file asynchronously.
    Move a file asynchronously.


    Args:
    Args:
    src_path: Path to the source file
    src_path: Path to the source file
    dest_path: Path where the file should be moved
    dest_path: Path where the file should be moved
    overwrite: Whether to overwrite the destination file if it exists
    overwrite: Whether to overwrite the destination file if it exists


    Raises:
    Raises:
    FileNotFoundError: If the source file doesn't exist
    FileNotFoundError: If the source file doesn't exist
    IOError: If there's an issue moving the file
    IOError: If there's an issue moving the file
    """
    """
    try:
    try:
    if not overwrite and await file_exists_async(dest_path):
    if not overwrite and await file_exists_async(dest_path):
    raise FileExistsError(f"Destination file already exists: {dest_path}")
    raise FileExistsError(f"Destination file already exists: {dest_path}")


    async with _file_lock:
    async with _file_lock:
    await run_in_thread(shutil.move, src_path, dest_path)
    await run_in_thread(shutil.move, src_path, dest_path)


    logger.debug(
    logger.debug(
    f"Successfully moved file asynchronously: {src_path} -> {dest_path}"
    f"Successfully moved file asynchronously: {src_path} -> {dest_path}"
    )
    )
except Exception as e:
except Exception as e:
    logger.error(f"Error in move_file_async: {e}")
    logger.error(f"Error in move_file_async: {e}")
    raise
    raise




    async def delete_file_async(file_path: str) -> None:
    async def delete_file_async(file_path: str) -> None:
    """
    """
    Delete a file asynchronously.
    Delete a file asynchronously.


    Args:
    Args:
    file_path: Path to the file to delete
    file_path: Path to the file to delete


    Raises:
    Raises:
    FileNotFoundError: If the file doesn't exist
    FileNotFoundError: If the file doesn't exist
    IOError: If there's an issue deleting the file
    IOError: If there's an issue deleting the file
    """
    """
    try:
    try:
    if not await file_exists_async(file_path):
    if not await file_exists_async(file_path):
    raise FileNotFoundError(f"File not found: {file_path}")
    raise FileNotFoundError(f"File not found: {file_path}")


    async with _file_lock:
    async with _file_lock:
    await run_in_thread(os.remove, file_path)
    await run_in_thread(os.remove, file_path)


    logger.debug(f"Successfully deleted file asynchronously: {file_path}")
    logger.debug(f"Successfully deleted file asynchronously: {file_path}")
except Exception as e:
except Exception as e:
    logger.error(f"Error in delete_file_async: {e}")
    logger.error(f"Error in delete_file_async: {e}")
    raise
    raise




    async def batch_process_files_async(
    async def batch_process_files_async(
    file_paths: List[str], process_func: callable, concurrency: int = 5, *args, **kwargs
    file_paths: List[str], process_func: callable, concurrency: int = 5, *args, **kwargs
    ) -> List[Any]:
    ) -> List[Any]:
    """
    """
    Process multiple files concurrently using an async function.
    Process multiple files concurrently using an async function.


    This utility is useful for batch processing multiple files such as reading,
    This utility is useful for batch processing multiple files such as reading,
    parsing, or analyzing file content in parallel.
    parsing, or analyzing file content in parallel.


    Args:
    Args:
    file_paths: List of file paths to process
    file_paths: List of file paths to process
    process_func: Async function that takes a file path and optional args
    process_func: Async function that takes a file path and optional args
    concurrency: Maximum number of concurrent operations
    concurrency: Maximum number of concurrent operations
    *args: Additional positional arguments to pass to process_func
    *args: Additional positional arguments to pass to process_func
    **kwargs: Additional keyword arguments to pass to process_func
    **kwargs: Additional keyword arguments to pass to process_func


    Returns:
    Returns:
    List of results from processing each file
    List of results from processing each file
    """
    """
    semaphore = asyncio.Semaphore(concurrency)
    semaphore = asyncio.Semaphore(concurrency)
    results = []
    results = []


    async def process_file(file_path):
    async def process_file(file_path):
    async with semaphore:
    async with semaphore:
    try:
    try:
    result = await process_func(file_path, *args, **kwargs)
    result = await process_func(file_path, *args, **kwargs)
    return {
    return {
    "file_path": file_path,
    "file_path": file_path,
    "result": result,
    "result": result,
    "success": True,
    "success": True,
    "error": None,
    "error": None,
    }
    }
except Exception as e:
except Exception as e:
    logger.error(f"Error processing file {file_path}: {e}")
    logger.error(f"Error processing file {file_path}: {e}")
    return {
    return {
    "file_path": file_path,
    "file_path": file_path,
    "result": None,
    "result": None,
    "success": False,
    "success": False,
    "error": str(e),
    "error": str(e),
    }
    }


    # Create tasks for all files
    # Create tasks for all files
    tasks = [process_file(file_path) for file_path in file_paths]
    tasks = [process_file(file_path) for file_path in file_paths]


    # Wait for all tasks to complete
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    results = await asyncio.gather(*tasks)
    return results
    return results




    async def read_files_batch_async(
    async def read_files_batch_async(
    file_paths: List[str],
    file_paths: List[str],
    binary: bool = False,
    binary: bool = False,
    encoding: str = "utf-8",
    encoding: str = "utf-8",
    concurrency: int = 5,
    concurrency: int = 5,
    ) -> List[dict]:
    ) -> List[dict]:
    """
    """
    Read multiple files concurrently.
    Read multiple files concurrently.


    This is a high-level utility that uses batch_process_files_async with read_file_async
    This is a high-level utility that uses batch_process_files_async with read_file_async
    to efficiently read multiple files in parallel.
    to efficiently read multiple files in parallel.


    Args:
    Args:
    file_paths: List of paths to files to read
    file_paths: List of paths to files to read
    binary: Whether to read in binary mode
    binary: Whether to read in binary mode
    encoding: Encoding to use when reading text files
    encoding: Encoding to use when reading text files
    concurrency: Maximum number of concurrent read operations
    concurrency: Maximum number of concurrent read operations


    Returns:
    Returns:
    List of dictionaries with file_path, content (result), success, and error information
    List of dictionaries with file_path, content (result), success, and error information
    """
    """


    async def read_file_wrapper(file_path):
    async def read_file_wrapper(file_path):
    return await read_file_async(file_path, binary, encoding)
    return await read_file_async(file_path, binary, encoding)


    return await batch_process_files_async(file_paths, read_file_wrapper, concurrency)
    return await batch_process_files_async(file_paths, read_file_wrapper, concurrency)




    async def write_files_batch_async(
    async def write_files_batch_async(
    file_contents: List[tuple],
    file_contents: List[tuple],
    binary: bool = False,
    binary: bool = False,
    encoding: str = "utf-8",
    encoding: str = "utf-8",
    create_dirs: bool = True,
    create_dirs: bool = True,
    concurrency: int = 5,
    concurrency: int = 5,
    ) -> List[dict]:
    ) -> List[dict]:
    """
    """
    Write content to multiple files concurrently.
    Write content to multiple files concurrently.


    Args:
    Args:
    file_contents: List of tuples (file_path, content) to write
    file_contents: List of tuples (file_path, content) to write
    binary: Whether to write in binary mode
    binary: Whether to write in binary mode
    encoding: Encoding to use when writing text
    encoding: Encoding to use when writing text
    create_dirs: Whether to create parent directories if they don't exist
    create_dirs: Whether to create parent directories if they don't exist
    concurrency: Maximum number of concurrent write operations
    concurrency: Maximum number of concurrent write operations


    Returns:
    Returns:
    List of dictionaries with file_path, success, and error information
    List of dictionaries with file_path, success, and error information
    """
    """
    semaphore = asyncio.Semaphore(concurrency)
    semaphore = asyncio.Semaphore(concurrency)
    results = []
    results = []


    async def write_file_wrapper(file_path, content):
    async def write_file_wrapper(file_path, content):
    async with semaphore:
    async with semaphore:
    try:
    try:
    await write_file_async(
    await write_file_async(
    file_path, content, binary, encoding, create_dirs
    file_path, content, binary, encoding, create_dirs
    )
    )
    return {"file_path": file_path, "success": True, "error": None}
    return {"file_path": file_path, "success": True, "error": None}
except Exception as e:
except Exception as e:
    logger.error(f"Error writing to file {file_path}: {e}")
    logger.error(f"Error writing to file {file_path}: {e}")
    return {"file_path": file_path, "success": False, "error": str(e)}
    return {"file_path": file_path, "success": False, "error": str(e)}


    # Create tasks for all files
    # Create tasks for all files
    tasks = [
    tasks = [
    write_file_wrapper(file_path, content) for file_path, content in file_contents
    write_file_wrapper(file_path, content) for file_path, content in file_contents
    ]
    ]


    # Wait for all tasks to complete
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    results = await asyncio.gather(*tasks)
    return results
    return results




    async def find_files_with_content_async(
    async def find_files_with_content_async(
    directory: str,
    directory: str,
    content_pattern: str,
    content_pattern: str,
    file_pattern: Optional[str] = None,
    file_pattern: Optional[str] = None,
    recursive: bool = True,
    recursive: bool = True,
    max_size_mb: float = 10.0,
    max_size_mb: float = 10.0,
    concurrency: int = 5,
    concurrency: int = 5,
    ) -> List[str]:
    ) -> List[str]:
    """
    """
    Find files containing specific content asynchronously.
    Find files containing specific content asynchronously.


    This function uses asynchronous processing to search through multiple files
    This function uses asynchronous processing to search through multiple files
    in parallel for specific content, which is much faster than sequential search
    in parallel for specific content, which is much faster than sequential search
    for large numbers of files.
    for large numbers of files.


    Args:
    Args:
    directory: Directory to search in
    directory: Directory to search in
    content_pattern: Content pattern to search for
    content_pattern: Content pattern to search for
    file_pattern: Optional pattern to filter files by name
    file_pattern: Optional pattern to filter files by name
    recursive: Whether to search recursively in subdirectories
    recursive: Whether to search recursively in subdirectories
    max_size_mb: Maximum file size in MB to consider
    max_size_mb: Maximum file size in MB to consider
    concurrency: Maximum number of concurrent search operations
    concurrency: Maximum number of concurrent search operations


    Returns:
    Returns:
    List of file paths containing the specified content
    List of file paths containing the specified content
    """
    """
    # First, list all files in the directory
    # First, list all files in the directory
    all_files = await list_files_async(directory, file_pattern, recursive)
    all_files = await list_files_async(directory, file_pattern, recursive)


    # Filter files by size to avoid processing very large files
    # Filter files by size to avoid processing very large files
    max_size_bytes = max_size_mb * 1024 * 1024
    max_size_bytes = max_size_mb * 1024 * 1024


    async def check_file_size_and_filter(file_path):
    async def check_file_size_and_filter(file_path):
    size = await get_file_size_async(file_path)
    size = await get_file_size_async(file_path)
    return size <= max_size_bytes
    return size <= max_size_bytes


    # Filter files by size concurrently
    # Filter files by size concurrently
    size_check_tasks = [check_file_size_and_filter(file) for file in all_files]
    size_check_tasks = [check_file_size_and_filter(file) for file in all_files]
    size_check_results = await asyncio.gather(*size_check_tasks)
    size_check_results = await asyncio.gather(*size_check_tasks)


    files_to_search = [
    files_to_search = [
    file for file, include in zip(all_files, size_check_results) if include
    file for file, include in zip(all_files, size_check_results) if include
    ]
    ]


    # Define a function to search a file for content
    # Define a function to search a file for content
    async def search_file_for_content(file_path):
    async def search_file_for_content(file_path):
    try:
    try:
    content = await read_file_async(file_path)
    content = await read_file_async(file_path)
    return content_pattern in content
    return content_pattern in content
except Exception:
except Exception:
    return False
    return False


    # Search for content in all files concurrently
    # Search for content in all files concurrently
    search_results = await batch_process_files_async(
    search_results = await batch_process_files_async(
    files_to_search, search_file_for_content, concurrency
    files_to_search, search_file_for_content, concurrency
    )
    )


    # Return only files that contain the content
    # Return only files that contain the content
    matching_files = [
    matching_files = [
    result["file_path"]
    result["file_path"]
    for result in search_results
    for result in search_results
    if result["success"] and result["result"]
    if result["success"] and result["result"]
    ]
    ]


    return matching_files
    return matching_files




    async def ensure_directory_exists_async(directory_path: str) -> bool:
    async def ensure_directory_exists_async(directory_path: str) -> bool:
    """
    """
    Ensure a directory exists, creating it if necessary.
    Ensure a directory exists, creating it if necessary.


    This is a convenience function that combines checking and creating a directory.
    This is a convenience function that combines checking and creating a directory.


    Args:
    Args:
    directory_path: Path to the directory
    directory_path: Path to the directory


    Returns:
    Returns:
    True if the directory exists or was created, False if it could not be created
    True if the directory exists or was created, False if it could not be created
    """
    """
    try:
    try:
    if await run_in_thread(os.path.isdir, directory_path):
    if await run_in_thread(os.path.isdir, directory_path):
    return True
    return True


    await create_directory_async(directory_path)
    await create_directory_async(directory_path)
    return True
    return True
except Exception as e:
except Exception as e:
    logger.error(f"Failed to ensure directory exists: {directory_path}, {e}")
    logger.error(f"Failed to ensure directory exists: {directory_path}, {e}")
    return False
    return False