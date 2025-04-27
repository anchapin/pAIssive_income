"""
File utilities for the pAIssive Income project.

This module provides common file handling functions used across the project.
"""

import os
import shutil
import logging
from typing import List, Optional, Union, BinaryIO, TextIO, Any

# Set up logging
logger = logging.getLogger(__name__)


def read_file(file_path: str, binary: bool = False, encoding: str = 'utf-8') -> Union[str, bytes]:
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
        mode = 'rb' if binary else 'r'
        kwargs = {} if binary else {'encoding': encoding}
        
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


def write_file(file_path: str, content: Union[str, bytes], binary: bool = False, 
               encoding: str = 'utf-8', create_dirs: bool = True) -> None:
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
        
        mode = 'wb' if binary else 'w'
        kwargs = {} if binary else {'encoding': encoding}
        
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


def list_files(directory: str, pattern: Optional[str] = None, 
               recursive: bool = False) -> List[str]:
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
                if os.path.isfile(file_path) and (pattern is None or pattern in filename):
                    files.append(file_path)
        
        return files
    except (FileNotFoundError, OSError) as e:
        logger.error(f"Error listing files in {directory}: {e}")
        raise


def list_directories(directory: str, pattern: Optional[str] = None, 
                    recursive: bool = False) -> List[str]:
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
