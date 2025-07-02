import pytest
from unittest.mock import patch
from promptshell.secure_storage import set_api_key, get_api_key, migrate_config_keys

@pytest.fixture
def mock_keyring():
    with patch("keyring.set_password") as mock_set, patch("keyring.get_password") as mock_get:
        mock_get.return_value = "test_key"
        yield mock_set, mock_get

def test_secure_storage(mock_keyring):
    set_api_key("TEST", "test_key")
    assert get_api_key("TEST") == "test_key"
    mock_keyring[0].assert_called_with("PromptShell", "TEST", "test_key")
    mock_keyring[1].assert_called_with("PromptShell", "TEST")

def test_migration(mocker):
    mock_config = {
        "GROQ_API_KEY": "groq_key",
        "OPENAI_API_KEY": "openai_key",
        "OTHER_KEY": "value"
    }
    mocker.patch("promptshell.secure_storage.set_api_key", return_value=True)
    migrated = migrate_config_keys(mock_config)
    
    assert migrated is True
    assert mock_config["GROQ_API_KEY"] == "🔒 SECURE_STORAGE"
    assert mock_config["OPENAI_API_KEY"] == "🔒 SECURE_STORAGE"
    assert mock_config["OTHER_KEY"] == "value"

def test_fallback_storage(capsys):
    with patch("keyring.set_password", side_effect=Exception("Test error")):
        result = set_api_key("FAIL", "test_key")
        captured = capsys.readouterr()
        
        assert "Secure storage failed" in captured.out
        assert result is False