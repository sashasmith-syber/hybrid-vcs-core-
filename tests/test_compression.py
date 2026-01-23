"""
Tests for compression utilities.
"""

import os
import tempfile
import pytest

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hybrid_vcs.compression import (
    compress_file, 
    decompress_data, 
    get_compression_ratio,
    estimate_compression_savings
)


class TestCompression:
    """Test cases for compression utilities."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def test_file(self, temp_dir):
        """Create a test file with compressible content."""
        file_path = os.path.join(temp_dir, "test_file.txt")
        # Create content with patterns that compress well
        content = "This is a test line that repeats.\n" * 1000
        with open(file_path, "w") as f:
            f.write(content)
        return file_path, content.encode()
    
    @pytest.fixture
    def binary_test_file(self, temp_dir):
        """Create a binary test file."""
        file_path = os.path.join(temp_dir, "test_binary.bin")
        # Create binary content with some patterns
        content = b"\x00\x01\x02\x03" * 2500  # 10KB of repeating pattern
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path, content
    
    def test_compress_file_text(self, test_file, temp_dir):
        """Test compressing a text file."""
        file_path, original_content = test_file
        output_path = os.path.join(temp_dir, "compressed.zst")
        
        content_hash = compress_file(file_path, output_path, level=6)
        
        # Verify output file exists
        assert os.path.exists(output_path)
        
        # Verify hash is correct length (SHA256)
        assert len(content_hash) == 64
        assert all(c in '0123456789abcdef' for c in content_hash)
        
        # Verify compression occurred (compressed should be smaller)
        original_size = os.path.getsize(file_path)
        compressed_size = os.path.getsize(output_path)
        assert compressed_size < original_size
    
    def test_compress_file_binary(self, binary_test_file, temp_dir):
        """Test compressing a binary file."""
        file_path, original_content = binary_test_file
        output_path = os.path.join(temp_dir, "compressed_binary.zst")
        
        content_hash = compress_file(file_path, output_path, level=3)
        
        # Verify output file exists
        assert os.path.exists(output_path)
        
        # Verify hash
        assert len(content_hash) == 64
        
        # Verify compression
        original_size = os.path.getsize(file_path)
        compressed_size = os.path.getsize(output_path)
        assert compressed_size < original_size
    
    def test_compress_nonexistent_file(self, temp_dir):
        """Test compressing a non-existent file."""
        nonexistent_path = os.path.join(temp_dir, "nonexistent.txt")
        output_path = os.path.join(temp_dir, "output.zst")
        
        with pytest.raises(FileNotFoundError):
            compress_file(nonexistent_path, output_path, level=6)
    
    def test_decompress_data(self, test_file, temp_dir):
        """Test decompressing data."""
        file_path, original_content = test_file
        output_path = os.path.join(temp_dir, "compressed.zst")
        
        # First compress the file
        compress_file(file_path, output_path, level=6)
        
        # Read compressed data
        with open(output_path, "rb") as f:
            compressed_data = f.read()
        
        # Decompress
        decompressed_data = decompress_data(compressed_data)
        
        # Verify decompressed data matches original
        assert decompressed_data == original_content
    
    def test_decompress_invalid_data(self):
        """Test decompressing invalid data."""
        invalid_data = b"This is not compressed data"
        
        with pytest.raises(Exception):  # Should raise zstandard error
            decompress_data(invalid_data)
    
    def test_compression_levels(self, test_file, temp_dir):
        """Test different compression levels."""
        file_path, _ = test_file
        
        sizes = {}
        for level in [1, 6, 11]:
            output_path = os.path.join(temp_dir, f"compressed_level_{level}.zst")
            compress_file(file_path, output_path, level=level)
            sizes[level] = os.path.getsize(output_path)
        
        # Higher compression levels should generally produce smaller files
        # (though this isn't guaranteed for all data types)
        assert sizes[1] >= sizes[6] >= sizes[11] or sizes[6] <= sizes[1]
    
    def test_get_compression_ratio(self):
        """Test compression ratio calculation."""
        # Test normal case
        ratio = get_compression_ratio(1000, 250)
        assert ratio == 4.0
        
        # Test edge case - zero compressed size
        ratio = get_compression_ratio(1000, 0)
        assert ratio == 0.0
        
        # Test no compression
        ratio = get_compression_ratio(1000, 1000)
        assert ratio == 1.0
    
    def test_estimate_compression_savings(self):
        """Test compression savings calculation."""
        # Test normal case
        bytes_saved, percent_saved = estimate_compression_savings(1000, 250)
        assert bytes_saved == 750
        assert percent_saved == 75.0
        
        # Test no compression
        bytes_saved, percent_saved = estimate_compression_savings(1000, 1000)
        assert bytes_saved == 0
        assert percent_saved == 0.0
        
        # Test edge case - zero original size
        bytes_saved, percent_saved = estimate_compression_savings(0, 0)
        assert bytes_saved == 0
        assert percent_saved == 0.0
        
        # Test expansion (compressed larger than original)
        bytes_saved, percent_saved = estimate_compression_savings(100, 150)
        assert bytes_saved == -50
        assert percent_saved == -50.0
    
    def test_round_trip_compression(self, binary_test_file, temp_dir):
        """Test complete round-trip compression and decompression."""
        file_path, original_content = binary_test_file
        compressed_path = os.path.join(temp_dir, "roundtrip.zst")
        
        # Compress
        content_hash = compress_file(file_path, compressed_path, level=6)
        
        # Read compressed data
        with open(compressed_path, "rb") as f:
            compressed_data = f.read()
        
        # Decompress
        decompressed_data = decompress_data(compressed_data)
        
        # Verify data integrity
        assert decompressed_data == original_content
        
        # Verify hash consistency
        import hashlib
        expected_hash = hashlib.sha256(original_content).hexdigest()
        assert content_hash == expected_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
