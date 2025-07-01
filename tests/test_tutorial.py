from unittest.mock import patch, MagicMock
from io import StringIO
from promptshell.main import main

def test_tutorial_command():
    """Test that entering --tutorial in the REPL launches the tutorial and prints the welcome message."""
    def input_side_effect(*args, **kwargs):
        responses = iter(['--tutorial', 'exit'])
        def inner(*args, **kwargs):
            try:
                return next(responses)
            except StopIteration:
                return 'exit'
        return inner

    with patch('builtins.input', side_effect=input_side_effect()), \
         patch('sys.stdout', new=StringIO()) as fake_out, \
         patch('questionary.confirm', return_value=MagicMock(ask=lambda: True)), \
         patch('os.get_terminal_size', return_value=(80, 24)):
        main()
        output = fake_out.getvalue()
        assert "Welcome to the interactive tutorial for PromptShell!" in output