import pytest
import os
from unittest.mock import patch, MagicMock
from promptshell.ai_terminal_assistant import AITerminalAssistant

@pytest.fixture
def assistant():
    return AITerminalAssistant(model_name="test-model")

@patch('promptshell.ai_terminal_assistant.questionary.confirm')
@patch('promptshell.ai_terminal_assistant.questionary.text')
@patch('os.get_terminal_size', return_value=os.terminal_size((80, 24)))
def test_confirm_safeguard_success(mock_terminal, mock_text, mock_confirm, assistant, capsys):
    user_input = "delete all files"
    generated_command = "CONFIRM:rm -rf *"

    assistant.command_executor = MagicMock(return_value=generated_command)

    mock_confirm.return_value.ask.return_value = True
    mock_text.return_value.ask.return_value = "rm -rf *"

    assistant.execute_command(user_input)
    captured = capsys.readouterr()

    assert "Command: rm -rf *" in captured.out


@patch('promptshell.ai_terminal_assistant.questionary.confirm')
@patch('promptshell.ai_terminal_assistant.questionary.text')
@patch('os.get_terminal_size', return_value=os.terminal_size((80, 24)))
def test_confirm_safeguard_mismatch(mock_terminal, mock_text, mock_confirm, assistant):
    user_input = "delete all files"
    generated_command = "CONFIRM:rm -rf *"

    assistant.command_executor = MagicMock(return_value=generated_command)

    mock_confirm.return_value.ask.return_value = True
    mock_text.return_value.ask.return_value = "rm -rf /wrong/path"

    result = assistant.execute_command(user_input)

    assert "Command mismatch" in result


@patch('promptshell.ai_terminal_assistant.questionary.confirm')
@patch('os.get_terminal_size', return_value=os.terminal_size((80, 24)))
def test_confirm_safeguard_first_cancel(mock_terminal, mock_confirm, assistant, capsys):
    user_input = "delete all files"
    generated_command = "CONFIRM:rm -rf *"

    assistant.command_executor = MagicMock(return_value=generated_command)
    mock_confirm.return_value.ask.return_value = False

    assistant.execute_command(user_input)
    captured = capsys.readouterr()

    assert "Command cancelled!" in captured.out
