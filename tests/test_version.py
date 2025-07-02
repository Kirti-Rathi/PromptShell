import sys
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from promptshell.main import main
import subprocess
from promptshell.version import get_version

class TestVersionFlag(unittest.TestCase):
    def test_version_flag(self):
        """Test that --version flag works and matches package version."""
        # Get version using our function
        expected_version = get_version()
        
        # Test with --version flag
        with patch('sys.argv', ['promptshell', '--version']), \
             patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            output = fake_out.getvalue().strip()
            self.assertEqual(output, f"PromptShell v{expected_version}")

    def test_version_matches_package(self):
        """Test that version matches the one in pyproject.toml."""
        version = get_version()
        self.assertNotEqual(version, "unknown", "Version should be properly detected")
        self.assertTrue(version.count('.') >= 1, "Version should be in format x.y.z")

def test_version_flag():
    """Test that --version flag works and matches package version."""
    # Get version using our function
    expected_version = get_version()
    
    # Run the command and capture output
    result = subprocess.run(
        [sys.executable, "-m", "promptshell", "--version"],
        capture_output=True,
        text=True
    )
    
    # Check if command was successful
    assert result.returncode == 0, f"Command failed with error: {result.stderr}"
    
    # Check if output matches expected format
    expected_output = f"PromptShell v{expected_version}"
    assert result.stdout.strip() == expected_output, \
        f"Expected '{expected_output}', got '{result.stdout.strip()}'"

if __name__ == '__main__':
    unittest.main() 