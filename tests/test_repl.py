import pytest
from io import StringIO
from unittest.mock import patch
from promptshell.main import main  # Adjust the import based on your project structure
import os

@patch('os.get_terminal_size', return_value=os.terminal_size((80, 24)))
@patch('builtins.input', side_effect=['exit'])
@patch('sys.stdout', new_callable=StringIO)
def test_exit_command(mock_stdout, mock_input, mock_terminal_size):
    """Test that the 'exit' command terminates the REPL session."""
    main()
    output = mock_stdout.getvalue()
    assert "Terminating..." in output  # Check for termination message

@patch('os.get_terminal_size', return_value=os.terminal_size((80, 24)))
@patch('builtins.input', side_effect=['quit'])
@patch('sys.stdout', new_callable=StringIO)
def test_quit_command(mock_stdout, mock_input, mock_terminal_size):
    """Test that the 'quit' command terminates the REPL session."""
    main()
    output = mock_stdout.getvalue()
    assert "Terminating..." in output  # Check for termination message
