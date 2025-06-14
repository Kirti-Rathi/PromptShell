import sys
import unittest
from unittest.mock import patch
from io import StringIO
from promptshell.main import main

class TestVersionFlag(unittest.TestCase):
    def test_version_flag(self):
        # Test with --version flag
        with patch('sys.argv', ['promptshell', '--version']), \
             patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            self.assertEqual(fake_out.getvalue().strip(), "PromptShell v0.1.1")

    def test_no_version_flag(self):
        # Test without --version flag
        with patch('sys.argv', ['promptshell']), \
             patch('sys.stdout', new=StringIO()) as fake_out, \
             patch('promptshell.main.load_config') as mock_load_config, \
             patch('promptshell.main.setup_wizard') as mock_setup_wizard:
            mock_load_config.return_value = {'MODE': 'local', 'LOCAL_MODEL': 'test-model'}
            main()
            self.assertNotEqual(fake_out.getvalue().strip(), "PromptShell v0.1.1")

if __name__ == '__main__':
    unittest.main() 