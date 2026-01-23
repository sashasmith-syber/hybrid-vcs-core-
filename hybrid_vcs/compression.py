"""
Compression utilities for Hybrid VCS.
"""

import hashlib
import zstandard
import logging
from typing import Tuple


def compress_file(file_path: str, output_path: str, level: int) -> str:
    """
    Compress a file using Zstandard compression in a separate process.
    
    Args:
        file_path: Path to the input file
        output_path: Path for the compressed output file
        level: Compression level (1-22, higher = better compression)
        
    Returns:
        SHA256 hash of the original file content
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        IOError: If there's an error reading/writing files
    """
    logger = logging.getLogger(__name__)
    
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        
        # Calculate hash of original data
        content_hash = hashlib.sha256(data).hexdigest()
        
        # Compress the data
        compressor = zstandard.ZstdCompressor(level=level)
        compressed_data = compressor.compress(data)
        
        # Write compressed data
        with open(output_path, "wb") as f:
            f.write(compressed_data)
        
        logger.debug(f"Compressed {file_path} -> {output_path} (hash: {content_hash[:8]}...)")
        return content_hash
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error compressing file {file_path}: {e}")
        raise


def decompress_data(compressed_data: bytes) -> bytes:
    """
    Decompress Zstandard compressed data.
    
    Args:
        compressed_data: Compressed data bytes
        
    Returns:
        Decompressed data bytes
        
    Raises:
        zstandard.ZstdError: If decompression fails
    """
    logger = logging.getLogger(__name__)
    
    try:
        decompressor = zstandard.ZstdDecompressor()
        decompressed_data = decompressor.decompress(compressed_data)
        logger.debug(f"Decompressed {len(compressed_data)} bytes -> {len(decompressed_data)} bytes")
        return decompressed_data
    except Exception as e:
        logger.error(f"Error decompressing data: {e}")
        raise


def get_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Calculate compression ratio.
    
    Args:
        original_size: Size of original data in bytes
        compressed_size: Size of compressed data in bytes
        
    Returns:
        Compression ratio (original_size / compressed_size)
    """
    if compressed_size == 0:
        return 0.0
    return original_size / compressed_size


def estimate_compression_savings(original_size: int, compressed_size: int) -> Tuple[int, float]:
    """
    Calculate compression savings.
    
    Args:
        original_size: Size of original data in bytes
        compressed_size: Size of compressed data in bytes
        
    Returns:
        Tuple of (bytes_saved, percentage_saved)
    """
    bytes_saved = original_size - compressed_size
    percentage_saved = (bytes_saved / original_size * 100) if original_size > 0 else 0.0
    return bytes_saved, percentage_saved
