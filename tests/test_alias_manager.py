import pytest
import json
from promptshell.alias_manager import AliasManager, handle_alias_command

# Use the fixture to ensure all tests in this class use a clean, temporary config directory.
@pytest.mark.usefixtures("mock_config_dir")
class TestAliasManager:
    def test_add_and_list_alias(self):
        manager = AliasManager()
        success, msg = manager.add_alias("ll", "ls -l", "list long")
        assert success
        assert msg == "Alias 'll' added"
        
        aliases = manager.list_aliases()
        assert "ll" in aliases
        assert aliases["ll"]["command"] == "ls -l"
        assert aliases["ll"]["description"] == "list long"

    def test_add_without_description(self):
        manager = AliasManager()
        success, msg = manager.add_alias("hello", "echo Hello")
        assert success
        assert msg == "Alias 'hello' added"

        aliases = manager.list_aliases()
        assert "hello" in aliases
        assert aliases["hello"]["command"] == "echo Hello"
        assert aliases["hello"]["description"] == ""

    def test_list_with_name(self):
        manager = AliasManager()
        success, msg = manager.add_alias("hello", "echo Hello")
        assert success
        assert msg == "Alias 'hello' added"

        aliases = manager.list_aliases('hello')
        assert aliases["command"] == "echo Hello"
        assert aliases["description"] == ""

    def test_remove_alias(self):
        manager = AliasManager()
        manager.add_alias("ll", "ls -l")
        
        success, msg = manager.remove_alias("ll")
        assert success
        assert msg == "Alias 'll' removed"
        assert "ll" not in manager.list_aliases()

    def test_add_alias_fails_on_duplicate(self):
        manager = AliasManager()
        manager.add_alias("ll", "ls -l")
        
        success, msg = manager.add_alias("ll", "ls -la")
        assert not success
        assert "Alias already exists" in msg 

    def test_add_alias_fails_on_dangerous_command(self):
        manager = AliasManager()
        success, msg = manager.add_alias("boom", "rm -rf /")
        assert not success
        assert "Invalid Command: Contains dangerous patterns" in msg

    def test_remove_alias_fails_if_not_found(self):
        manager = AliasManager()
        success, msg = manager.remove_alias("nonexistent")
        assert not success
        assert "Alias not found" in msg

    def test_expand_alias(self):
        manager = AliasManager()
        manager.add_alias("gs", "git status")
        
        expanded = manager.expand_alias("gs")
        assert expanded == "git status"
        
        expanded_with_args = manager.expand_alias("gs -s")
        assert expanded_with_args == "git status -s"
        
        # Test that non-aliases are not expanded
        not_expanded = manager.expand_alias("ls -l")
        assert not_expanded == "ls -l"

    def test_save_and_load_aliases(self, mock_config_dir):
        # First session: add and save
        manager1 = AliasManager()
        manager1.add_alias("gco", "git checkout", "changes git branch")
        manager1.save_aliases()

        # Check if the file was actually written
        alias_file = f"{mock_config_dir}/aliases.json"
        with open(alias_file, 'r') as f:
            data = json.load(f)
            assert "gco" in data["aliases"]

        # Second session: new manager should load from the file
        manager2 = AliasManager()
        assert "gco" in manager2.list_aliases()
        assert manager2.list_aliases("gco")["command"] == "git checkout"
        assert manager2.list_aliases('gco')["description"] == "changes git branch"

def test_handle_alias_command_add(mocker):
    # Mock the AliasManager instance that the handler function will use
    mock_manager = mocker.MagicMock(spec=AliasManager)
    
    # Simulate the shlex.split output for "alias add ll 'ls -l'"
    command_str = 'alias add ll "ls -l" --desc "show list"'
    
    handle_alias_command(command_str, mock_manager)
    
    # Assert that the correct method was called on our mock manager
    mock_manager.add_alias.assert_called_once_with("ll", "ls -l", "show list")

def test_handle_alias_command_help(mocker):
    mock_manager = mocker.MagicMock(spec=AliasManager)
    result = handle_alias_command("alias help", mock_manager)
    assert "Alias Management Commands:" in result