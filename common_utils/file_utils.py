"""
File utilities for the pAIssive Income project.

This module provides common file handling functions used across the project.
"""

import os
import shutil
import logging
import asyncio
from typing import List, Optional, Union, Any

# Import the run_in_thread utility for async operations
from ai_models.async_utils import run_in_thread

# Set up logging
logger = logging.getLogger(__name__)

# Async file operation lock for concurrent access control
_file_lock = asyncio.Lock()


def read_file(
    file_path: str, binary: bool = False, encoding: str = "utf-8"
) -> Union[str, bytes]:
    """
    Read content from a file.

    Args:
        file_path: Path to the file
        binary: Whether to read in binary mode (default: False)
        encoding: Encoding to use when reading text (default: utf-8)

    Returns:
        File content as string or bytes

    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an issue reading the file
    """
    try:
        mode = "rb" if binary else "r"
        kwargs = {} if binary else {"encoding": encoding}

        with open(file_path, mode, **kwargs) as f:
            content = f.read()

        logger.debug(f"Successfully read file: {file_path}")
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except (IOError, OSError) as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def write_file(
    file_path: str,
    content: Union[str, bytes],
    binary: bool = False,
    encoding: str = "utf-8",
    create_dirs: bool = True,
) -> None:
    """
    Write content to a file.

    Args:
        file_path: Path to the file
        content: Content to write
        binary: Whether to write in binary mode (default: False)
        encoding: Encoding to use when writing text (default: utf-8)
        create_dirs: Whether to create parent directories if they don't exist (default: True)

    Raises:
        IOError: If there's an issue writing to the file
    """
    try:
        # Create parent directories if they don't exist
        if create_dirs:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

        mode = "wb" if binary else "w"
        kwargs = {} if binary else {"encoding": encoding}

        with open(file_path, mode, **kwargs) as f:
            f.write(content)

        logger.debug(f"Successfully wrote to file: {file_path}")
    except (IOError, OSError) as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise


def file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path: Path to the file

    Returns:
        True if the file exists, False otherwise
    """
    return os.path.isfile(file_path)


def create_directory(directory_path: str, exist_ok: bool = True) -> None:
    """
    Create a directory.

    Args:
        directory_path: Path to the directory
        exist_ok: Whether to ignore if the directory already exists (default: True)

    Raises:
        OSError: If there's an issue creating the directory
    """
    try:
        os.makedirs(directory_path, exist_ok=exist_ok)
        logger.debug(f"Successfully created directory: {directory_path}")
    except OSError as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        raise


def get_file_path(directory: str, filename: str) -> str:
    """
    Get the full path to a file.

    Args:
        directory: Directory path
        filename: File name

    Returns:
        Full path to the file
    """
    return os.path.join(directory, filename)


def get_directory_path(base_dir: str, *subdirs: str) -> str:
    """
    Get the full path to a directory.

    Args:
        base_dir: Base directory path
        *subdirs: Subdirectories

    Returns:
        Full path to the directory
    """
    return os.path.join(base_dir, *subdirs)


def list_files(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
) -> List[str]:
    """
    List files in a directory.

    Args:
        directory: Directory path
        pattern: File pattern to match (default: None)
        recursive: Whether to search recursively (default: False)

    Returns:
        List of file paths

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    try:
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = []

        if recursive:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if pattern is None or pattern in filename:
                        files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) and (
                    pattern is None or pattern in filename
                ):
                    files.append(file_path)

        return files
    except (FileNotFoundError, OSError) as e:
        logger.error(f"Error listing files in {directory}: {e}")
        raise


def list_directories(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
) -> List[str]:
    """
    List subdirectories in a directory.

    Args:
        directory: Directory path
        pattern: Directory pattern to match (default: None)
        recursive: Whether to search recursively (default: False)

    Returns:
        List of directory paths

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    try:
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        directories = []

        if recursive:
            for root, dirs, _ in os.walk(directory):
                for dir_name in dirs:
                    if pattern is None or pattern in dir_name:
                        directories.append(os.path.join(root, dir_name))
        else:
            for dir_name in os.listdir(directory):
                dir_path = os.path.join(directory, dir_name)
                if os.path.isdir(dir_path) and (pattern is None or pattern in dir_name):
                    directories.append(dir_path)

        return directories
    except (FileNotFoundError, OSError) as e:
        logger.error(f"Error listing directories in {directory}: {e}")
        raise


def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.

    Args:
        file_path: Path to the file

    Returns:
        File extension (without the dot)
    """
    return os.path.splitext(file_path)[1][1:]


def get_file_name(file_path: str, with_extension: bool = True) -> str:
    """
    Get the name of a file.

    Args:
        file_path: Path to the file
        with_extension: Whether to include the extension (default: True)

    Returns:
        File name
    """
    if with_extension:
        return os.path.basename(file_path)
    return os.path.splitext(os.path.basename(file_path))[0]


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    try:
        return os.path.getsize(file_path)
    except (FileNotFoundError, OSError) as e:
        logger.error(f"Error getting size of file {file_path}: {e}")
        raise


async def read_file_async(
    file_path: str, binary: bool = False, encoding: str = "utf-8"
) -> Union[str, bytes]:
    """
    Read content from a file asynchronously.

    This is the asynchronous version of read_file() that doesn't block the
    main event loop during file I/O operations.

    Args:
        file_path: Path to the file
        binary: Whether to read in binary mode (default: False)
        encoding: Encoding to use when reading text (default: utf-8)

    Returns:
        File content as string or bytes

    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an issue reading the file
    """
    # Use run_in_thread to run the blocking I/O operation in a thread pool
    try:
        async with _file_lock:
            return await run_in_thread(read_file, file_path, binary, encoding)
    except Exception as e:
        logger.error(f"Error in read_file_async for {file_path}: {e}")
        raise


async def write_file_async(
    file_path: str,
    content: Union[str, bytes],
    binary: bool = False,
    encoding: str = "utf-8",
    create_dirs: bool = True,
) -> None:
    """
    Write content to a file asynchronously.

    This is the asynchronous version of write_file() that doesn't block the
    main event loop during file I/O operations.

    Args:
        file_path: Path to the file
        content: Content to write
        binary: Whether to write in binary mode (default: False)
        encoding: Encoding to use when writing text (default: utf-8)
        create_dirs: Whether to create parent directories if they don't exist (default: True)

    Raises:
        IOError: If there's an issue writing to the file
    """
    try:
        async with _file_lock:
            await run_in_thread(
                write_file, file_path, content, binary, encoding, create_dirs
            )
        logger.debug(f"Successfully wrote to file asynchronously: {file_path}")
    except Exception as e:
        logger.error(f"Error in write_file_async for {file_path}: {e}")
        raise


async def file_exists_async(file_path: str) -> bool:
    """
    Check if a file exists asynchronously.

    This is the asynchronous version of file_exists() that doesn't block the
    main event loop during file I/O operations.

    Args:
        file_path: Path to the file

    Returns:
        True if the file exists, False otherwise
    """
    return await run_in_thread(os.path.isfile, file_path)


async def create_directory_async(directory_path: str, exist_ok: bool = True) -> None:
    """
    Create a directory asynchronously.

    This is the asynchronous version of create_directory() that doesn't block the
    main event loop during file I/O operations.

    Args:
        directory_path: Path to the directory
        exist_ok: Whether to ignore if the directory already exists (default: True)

    Raises:
        OSError: If there's an issue creating the directory
    """
    try:
        await run_in_thread(create_directory, directory_path, exist_ok)
        logger.debug(f"Successfully created directory asynchronously: {directory_path}")
    except Exception as e:
        logger.error(f"Error in create_directory_async for {directory_path}: {e}")
        raise


async def list_files_async(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
) -> List[str]:
    """
    List files in a directory asynchronously.

    This is the asynchronous version of list_files() that doesn't block the
    main event loop during file I/O operations, which is particularly beneficial
    for large directories or network file systems.

    Args:
        directory: Directory path
        pattern: File pattern to match (default: None)
        recursive: Whether to search recursively (default: False)

    Returns:
        List of file paths

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    return await run_in_thread(list_files, directory, pattern, recursive)


async def list_directories_async(
    directory: str, pattern: Optional[str] = None, recursive: bool = False
) -> List[str]:
    """
    List subdirectories in a directory asynchronously.

    This is the asynchronous version of list_directories() that doesn't block the
    main event loop during file I/O operations, which is particularly beneficial
    for large directories or network file systems.

    Args:
        directory: Directory path
        pattern: Directory pattern to match (default: None)
        recursive: Whether to search recursively (default: False)

    Returns:
        List of directory paths

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    return await run_in_thread(list_directories, directory, pattern, recursive)


async def get_file_size_async(file_path: str) -> int:
    """
    Get the size of a file in bytes asynchronously.

    This is the asynchronous version of get_file_size() that doesn't block the
    main event loop during file I/O operations.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    return await run_in_thread(get_file_size, file_path)


async def copy_file_async(
    src_path: str, dest_path: str, overwrite: bool = False
) -> None:
    """
    Copy a file asynchronously.

    Args:
        src_path: Path to the source file
        dest_path: Path where the file should be copied
        overwrite: Whether to overwrite the destination file if it exists

    Raises:
        FileNotFoundError: If the source file doesn't exist
        IOError: If there's an issue copying the file
    """
    try:
        if not overwrite and await file_exists_async(dest_path):
            raise FileExistsError(f"Destination file already exists: {dest_path}")

        async with _file_lock:
            await run_in_thread(shutil.copy2, src_path, dest_path)

        logger.debug(
            f"Successfully copied file asynchronously: {src_path} -> {dest_path}"
        )
    except Exception as e:
        logger.error(f"Error in copy_file_async: {e}")
        raise


async def move_file_async(
    src_path: str, dest_path: str, overwrite: bool = False
) -> None:
    """
    Move a file asynchronously.

    Args:
        src_path: Path to the source file
        dest_path: Path where the file should be moved
        overwrite: Whether to overwrite the destination file if it exists

    Raises:
        FileNotFoundError: If the source file doesn't exist
        IOError: If there's an issue moving the file
    """
    try:
        if not overwrite and await file_exists_async(dest_path):
            raise FileExistsError(f"Destination file already exists: {dest_path}")

        async with _file_lock:
            await run_in_thread(shutil.move, src_path, dest_path)

        logger.debug(
            f"Successfully moved file asynchronously: {src_path} -> {dest_path}"
        )
    except Exception as e:
        logger.error(f"Error in move_file_async: {e}")
        raise


async def delete_file_async(file_path: str) -> None:
    """
    Delete a file asynchronously.

    Args:
        file_path: Path to the file to delete

    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an issue deleting the file
    """
    try:
        if not await file_exists_async(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        async with _file_lock:
            await run_in_thread(os.remove, file_path)

        logger.debug(f"Successfully deleted file asynchronously: {file_path}")
    except Exception as e:
        logger.error(f"Error in delete_file_async: {e}")
        raise


async def batch_process_files_async(
    file_paths: List[str], process_func: callable, concurrency: int = 5, *args, **kwargs
) -> List[Any]:
    """
    Process multiple files concurrently using an async function.

    This utility is useful for batch processing multiple files such as reading,
    parsing, or analyzing file content in parallel.

    Args:
        file_paths: List of file paths to process
        process_func: Async function that takes a file path and optional args
        concurrency: Maximum number of concurrent operations
        *args: Additional positional arguments to pass to process_func
        **kwargs: Additional keyword arguments to pass to process_func

    Returns:
        List of results from processing each file
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def process_file(file_path):
        async with semaphore:
            try:
                result = await process_func(file_path, *args, **kwargs)
                return {
                    "file_path": file_path,
                    "result": result,
                    "success": True,
                    "error": None,
                }
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                return {
                    "file_path": file_path,
                    "result": None,
                    "success": False,
                    "error": str(e),
                }

    # Create tasks for all files
    tasks = [process_file(file_path) for file_path in file_paths]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    return results


async def read_files_batch_async(
    file_paths: List[str],
    binary: bool = False,
    encoding: str = "utf-8",
    concurrency: int = 5,
) -> List[dict]:
    """
    Read multiple files concurrently.

    This is a high-level utility that uses batch_process_files_async with read_file_async
    to efficiently read multiple files in parallel.

    Args:
        file_paths: List of paths to files to read
        binary: Whether to read in binary mode
        encoding: Encoding to use when reading text files
        concurrency: Maximum number of concurrent read operations

    Returns:
        List of dictionaries with file_path, content (result), success, and error information
    """

    async def read_file_wrapper(file_path):
        return await read_file_async(file_path, binary, encoding)

    return await batch_process_files_async(file_paths, read_file_wrapper, concurrency)


async def write_files_batch_async(
    file_contents: List[tuple],
    binary: bool = False,
    encoding: str = "utf-8",
    create_dirs: bool = True,
    concurrency: int = 5,
) -> List[dict]:
    """
    Write content to multiple files concurrently.

    Args:
        file_contents: List of tuples (file_path, content) to write
        binary: Whether to write in binary mode
        encoding: Encoding to use when writing text
        create_dirs: Whether to create parent directories if they don't exist
        concurrency: Maximum number of concurrent write operations

    Returns:
        List of dictionaries with file_path, success, and error information
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def write_file_wrapper(file_path, content):
        async with semaphore:
            try:
                await write_file_async(
                    file_path, content, binary, encoding, create_dirs
                )
                return {"file_path": file_path, "success": True, "error": None}
            except Exception as e:
                logger.error(f"Error writing to file {file_path}: {e}")
                return {"file_path": file_path, "success": False, "error": str(e)}

    # Create tasks for all files
    tasks = [
        write_file_wrapper(file_path, content) for file_path, content in file_contents
    ]

    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks)
    return results


async def find_files_with_content_async(
    directory: str,
    content_pattern: str,
    file_pattern: Optional[str] = None,
    recursive: bool = True,
    max_size_mb: float = 10.0,
    concurrency: int = 5,
) -> List[str]:
    """
    Find files containing specific content asynchronously.

    This function uses asynchronous processing to search through multiple files
    in parallel for specific content, which is much faster than sequential search
    for large numbers of files.

    Args:
        directory: Directory to search in
        content_pattern: Content pattern to search for
        file_pattern: Optional pattern to filter files by name
        recursive: Whether to search recursively in subdirectories
        max_size_mb: Maximum file size in MB to consider
        concurrency: Maximum number of concurrent search operations

    Returns:
        List of file paths containing the specified content
    """
    # First, list all files in the directory
    all_files = await list_files_async(directory, file_pattern, recursive)

    # Filter files by size to avoid processing very large files
    max_size_bytes = max_size_mb * 1024 * 1024

    async def check_file_size_and_filter(file_path):
        size = await get_file_size_async(file_path)
        return size <= max_size_bytes

    # Filter files by size concurrently
    size_check_tasks = [check_file_size_and_filter(file) for file in all_files]
    size_check_results = await asyncio.gather(*size_check_tasks)

    files_to_search = [
        file for file, include in zip(all_files, size_check_results) if include
    ]

    # Define a function to search a file for content
    async def search_file_for_content(file_path):
        try:
            content = await read_file_async(file_path)
            return content_pattern in content
        except Exception:
            return False

    # Search for content in all files concurrently
    search_results = await batch_process_files_async(
        files_to_search, search_file_for_content, concurrency
    )

    # Return only files that contain the content
    matching_files = [
        result["file_path"]
        for result in search_results
        if result["success"] and result["result"]
    ]

    return matching_files


async def ensure_directory_exists_async(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    This is a convenience function that combines checking and creating a directory.

    Args:
        directory_path: Path to the directory

    Returns:
        True if the directory exists or was created, False if it could not be created
    """
    try:
        if await run_in_thread(os.path.isdir, directory_path):
            return True

        await create_directory_async(directory_path)
        return True
    except Exception as e:
        logger.error(f"Failed to ensure directory exists: {directory_path}, {e}")
        return False
