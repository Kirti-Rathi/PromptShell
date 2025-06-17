import json
import os
import re
from datetime import datetime
from .setup import CONFIG_DIR
import shlex
from pathlib import Path
from .format_utils import format_text, reset_format

ALIAS_FILE = os.path.join(CONFIG_DIR, "aliases.json")

class AliasManager:
    """
    Manages alias commands for the terminal assistant. Handles adding, removing,
    listing, importing, exporting, and expanding command aliases.
    """
    def __init__(self):
        """
        Initializes the AliasManager and loads any existing aliases from file.
        """
        self.aliases = {}
        self.blacklist = ["rm -rf /", "chmod -R 777 /", ":(){:|:&};:", "mkfs", "dd if=/dev/random"]
        self.load_aliases()
    
    def load_aliases(self):
        """
        Loads aliases from the JSON alias file.
        """
        if os.path.exists(ALIAS_FILE):
            try:
                with open(ALIAS_FILE, 'r') as f:
                    data = json.load(f)
                    self.aliases = data.get('aliases', {})
            except (json.JSONDecodeError, IOError):
                self.aliases = {}
    
    def save_aliases(self):
        """
        Saves the current aliases to the JSON alias file.
        """
        with open(ALIAS_FILE, 'w') as f:
            json.dump({'aliases': self.aliases}, f, indent=2)
    
    def validate_alias_name(self, name):
        """
        Validates an alias name using a regex pattern.

        Args:
            name (str): Alias name.

        Returns:
            bool: True if valid, False otherwise.
        """
        return re.match(r'^[a-zA-Z_]\w*$', name) is not None
    
    def validate_command(self, command):
        """
        Validates a command to ensure it does not contain dangerous operations.

        Args:
            command (str): Shell command.

        Returns:
            bool: True if safe, False otherwise.
        """
        for dangerous in self.blacklist:
            if dangerous in command:
                return False
        return True
    
    def add_alias(self, name, command, description=""):
        """
        Adds a new alias to the alias list.

        Args:
            name (str): Alias name.
            command (str): Shell command.
            description (str): Optional description.

        Returns:
            tuple: (bool, message) indicating success or failure.
        """
        if not self.validate_alias_name(name):
            return False, f"{format_text("red")}Invalid alias name: Name must be alphanumeric with underscores{reset_format()}"
        
        if not self.validate_command(command):
            return False, f"{format_text("red", bold=True)}Invalid Command: Contains dangerous patterns{reset_format()}"
        
        if name in self.aliases:
            return False, f"{format_text("red")}Duplicate alias name: Alias already exists{reset_format()}"
        
        self.aliases[name] = {
            'command': command,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.save_aliases()
        return True, f"Alias '{name}' added"
    
    def remove_alias(self, name):
        """
        Removes an alias by name.

        Args:
            name (str): Alias name.

        Returns:
            tuple: (bool, message) indicating result.
        """
        if name not in self.aliases:
            return False, f"{format_text("red")}Alias not found{reset_format()}"
        
        del self.aliases[name]
        self.save_aliases()
        return True, f"Alias '{name}' removed"
    
    def list_aliases(self, name=None):
        """
        Lists all aliases or a specific one by name.

        Args:
            name (str, optional): Alias name.

        Returns:
            dict or None: Alias details or all aliases.
        """
        if name:
            return self.aliases.get(name, None)
        return self.aliases
    
    

    def import_aliases(self, file_path):
        """
        Imports aliases from a JSON file.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            tuple: (bool, message) indicating result.
        """
        file_path = os.path.expanduser(file_path)  # Handles ~
        path_obj = Path(file_path)

        if not path_obj.exists() or not path_obj.is_file():
            return False, f"{format_text("red")}Import error: File '{file_path}' not found.{reset_format()}"

        try:
            with open(path_obj, 'r') as f:
                data = json.load(f)
                for name, alias_data in data.get('aliases', {}).items():
                    if self.validate_alias_name(name) and self.validate_command(alias_data.get('command', '')):
                        self.aliases[name] = alias_data
            self.save_aliases()
            return True, "Aliases imported successfully"
        except json.JSONDecodeError:
            return False, f"{format_text("red")}Invalid JSON: Incorrect JSON format in alias file{reset_format()}."
        except Exception as e:
            return False, f"{format_text("red")}Import error: Failed to import aliases: {str(e)}{reset_format()}"

    
    
    def export_aliases(self, file_path):
        """
        Exports current aliases to a JSON file.

        Args:
            file_path (str): Destination file path.

        Returns:
            tuple: (bool, message) indicating result.
        """
        try:
            with open(file_path, 'w') as f:
                json.dump({'aliases': self.aliases}, f, indent=2)
            return True, "Aliases exported successfully"
        except Exception as e:
            return False, f"{format_text("red")}Export failed: {str(e)}{reset_format()}"
    
    def expand_alias(self, input_command):
        """
        Expands a command if it matches a defined alias.

        Args:
            input_command (str): Command entered by user.

        Returns:
            str: Expanded command or original input.
        """
        parts = input_command.strip().split(maxsplit=1)
        if not parts:
            return input_command
        
        alias_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        if alias_name in self.aliases:
            base_command = self.aliases[alias_name]['command']
            return f"{base_command} {args}".strip()
        return input_command

def handle_alias_command(command: str, alias_manager: AliasManager) -> str:
    """
    Handles CLI interaction for managing aliases.

    Args:
        command (str): Full alias command input from user.
        alias_manager (AliasManager): Instance of AliasManager.

    Returns:
        str: Result message or error description.
    """
    try:
        parts = shlex.split(command)
        if len(parts) < 2:
            return f"{format_text("white", bold=True)}Usage: alias [add|remove|list|import|export|help]{reset_format()}"
        
        subcommand = parts[1].lower()
        
        if subcommand == "add" and len(parts) >= 4:
            name = parts[2]
            cmd = " ".join(parts[3:])
            _, message = alias_manager.add_alias(name, cmd)
            return message
        
        elif subcommand == "remove" and len(parts) >= 3:
            _, message = alias_manager.remove_alias(parts[2])
            return message
        
        elif subcommand == "list":
            if len(parts) >= 3:
                alias = alias_manager.list_aliases(parts[2])
                if alias:
                    return f"{parts[2]}: {alias['command']}\nDescription: {alias.get('description', '')}"
                return f"{format_text("red")}Invalid alias name: Alias not found{reset_format()}"
            aliases = alias_manager.list_aliases()
            return "\n".join([f"{name}: {data['command']}" for name, data in aliases.items()])
        
        elif subcommand == "import" and len(parts) >= 3:
            _, message = alias_manager.import_aliases(parts[2])
            return message
        
        elif subcommand == "export" and len(parts) >= 3:
            _, message = alias_manager.export_aliases(parts[2])
            return message
        
        elif subcommand == "help":
            return (
                "Alias Management Commands:\n"
                "  alias add <name> \"<command>\" - Add new alias\n"
                "  alias remove <name> - Remove alias\n"
                "  alias list [name] - List all aliases or show details\n"
                "  alias import <file> - Import aliases from JSON file\n"
                "  alias export <file> - Export aliases to JSON file\n"
                "  alias help - Show this help"
            )
        
        return f"{format_text("red")}Invalid alias command: Use alias help for valid all commands{reset_format()}"
    except Exception as e:
        return f"{format_text("red")}Error processing alias command: {str(e)}{reset_format()}"