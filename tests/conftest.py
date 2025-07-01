import pytest
import os

@pytest.fixture
def mock_config_dir(tmp_path, mocker):
    """
    tmp_path creates a temporary config directory and mocks the constants in the
    setup and alias_manager modules to use it.
    """

    # Create a temporary directory for the test
    temp_dir = tmp_path / "config"
    temp_dir.mkdir()

    # Mock the constants in the modules where they are defined
    mocker.patch('promptshell.setup.CONFIG_DIR', str(temp_dir))
    mocker.patch('promptshell.alias_manager.CONFIG_DIR', str(temp_dir))

    # The ALIAS_FILE is derived from CONFIG_DIR, so we must update it too
    mocker.patch('promptshell.alias_manager.ALIAS_FILE', os.path.join(str(temp_dir), "aliases.json"))
    return str(temp_dir)
