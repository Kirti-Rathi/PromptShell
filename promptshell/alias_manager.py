import json
import os
import re
import questionary
from datetime import datetime
from .setup import CONFIG_DIR
import shlex
from pathlib import Path
from .format_utils import format_text, reset_format

ALIAS_FILE = os.path.join(CONFIG_DIR, "aliases.json")

class AliasManager:
    def __init__(self):
        """Manages shell command aliases."""

        self.aliases = {}
        self.blacklist = ["rm -rf /", "chmod -R 777 /", ":(){:|:&};:", "mkfs", "dd if=/dev/random"]
        self.load_aliases()
    
    def load_aliases(self):
        """Loads aliases from persistent storage."""

        if os.path.exists(ALIAS_FILE):
            try:
                with open(ALIAS_FILE, 'r') as f:
                    data = json.load(f)
                    self.aliases = data.get('aliases', {})
            except (json.JSONDecodeError, IOError):
                self.aliases = {}
    
    def save_aliases(self):
        """Saves aliases to persistent storage."""

        with open(ALIAS_FILE, 'w') as f:
            json.dump({'aliases': self.aliases}, f, indent=2)
    
    def validate_alias_name(self, name):
        """Validates alias name format.
        
        Args:
            name: Alias name to validate
            
        Returns:
            True if valid, False otherwise
        """

        return re.match(r'^[a-zA-Z_]\w*$', name) is not None
    
    def validate_command(self, command):
        """Checks for dangerous commands.
        
        Args:
            command: Command to validate
            
        Returns:
            True if safe, False otherwise
        """

        for dangerous in self.blacklist:
            if dangerous in command:
                return False
        return True
    
    def add_alias(self, name, command, description=""):
        """Adds a new command alias.
        
        Args:
            name: Alias name
            command: Command to execute
            description: Optional description
            
        Returns:
            Tuple (success status, message)
        """

        if not self.validate_alias_name(name):
            return False, f"{format_text('red')}Invalid alias name: Name must be alphanumeric with underscores{reset_format()}"
        
        if not self.validate_command(command):
            return False, f"{format_text('red', bold=True)}Invalid Command: Contains dangerous patterns{reset_format()}"
        
        if name in self.aliases:
            return False, f"{format_text('red')}Duplicate alias name: Alias already exists{reset_format()}"
        
        self.aliases[name] = {
            'command': command,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self.save_aliases()
        return True, f"Alias '{name}' added"
    
    def remove_alias(self, name):
        """Removes an existing alias.
        
        Args:
            name: Alias name to remove
            
        Returns:
            Tuple (success status, message)
        """

        if name not in self.aliases:
            return False, f"{format_text('red')}Alias not found{reset_format()}"
        
        del self.aliases[name]
        self.save_aliases()
        return True, f"Alias '{name}' removed"
    
    def list_aliases(self, name=None):
        """Lists registered aliases.
        
        Args:
            name: Optional specific alias to look up
            
        Returns:
            Dictionary of aliases or single alias details
        """

        if name:
            return self.aliases.get(name, None)
        return self.aliases
    
    

    def import_aliases(self, file_path):
        """Imports aliases from JSON file.
        
        Args:
            file_path: Path to import file
            
        Returns:
            Tuple (success status, message)
        """

        file_path = os.path.expanduser(file_path)  # Handles ~
        path_obj = Path(file_path)

        if not path_obj.exists() or not path_obj.is_file():
            return False, f"{format_text('red')}Import error: File '{file_path}' not found.{reset_format()}"

        try:
            with open(path_obj, 'r') as f:
                data = json.load(f)
                for name, alias_data in data.get('aliases', {}).items():
                    if self.validate_alias_name(name) and self.validate_command(alias_data.get('command', '')):
                        self.aliases[name] = alias_data
            self.save_aliases()
            return True, "Aliases imported successfully"
        except json.JSONDecodeError:
            return False, f"{format_text('red')}Invalid JSON: Incorrect JSON format in alias file{reset_format()}."
        except Exception as e:
            return False, f"{format_text('red')}Import error: Failed to import aliases: {str(e)}{reset_format()}"

    
    
    def export_aliases(self, file_path):
        """Exports aliases to JSON file.
        
        Args:
            file_path: Export file path
            
        Returns:
            Tuple (success status, message)
        """

        try:
            with open(file_path, 'w') as f:
                json.dump({'aliases': self.aliases}, f, indent=2)
            return True, "Aliases exported successfully"
        except Exception as e:
            return False, f"{format_text('red')}Export failed: {str(e)}{reset_format()}"
    
    def expand_alias(self, input_command):
        """Expands aliases in commands.
        
        Args:
            input_command: Command potentially containing aliases
            
        Returns:
            Expanded command string
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
    
    def clear_all_alias(self):
        confirm = questionary.confirm("Are you sure you want to remove all aliases?").ask()
        
        if not confirm:
            return False, "Alias clear operation cancelled."
        
        self.aliases = {}
        
        # file existence check
        if not os.path.exists(ALIAS_FILE):
            return False, "Alias file not found."
        
        with open(ALIAS_FILE, 'w') as f:
            json.dump({'aliases': self.aliases}, f, indent=2)
        
        return True,"All aliases cleared."
        
        

def handle_alias_command(command: str, alias_manager: AliasManager) -> str:
    """Processes alias management commands.
    
    Args:
        command: Full alias command string
        alias_manager: AliasManager instance
        
    Returns:
        Command execution result message
    """
    
    try:
        parts = shlex.split(command)
        if len(parts) < 2:
            return f"{format_text('white', bold=True)}Usage: alias [add|remove|list|import|export|help]{reset_format()}"
        
        subcommand = parts[1].lower()
        
        if subcommand == "add":
            if len(parts) < 4:
                raise ValueError("atleast 4 parts required.")
            name = parts[2]
            cmd = parts[3]
            if len(parts) == 4:
                _, message = alias_manager.add_alias(name, cmd)
                return message
            elif parts[4] == "--desc":
                desc = parts[5] if len(parts)>5 else "" 
                _, message = alias_manager.add_alias(name, cmd, desc)
                return message
        
        elif subcommand == "remove" and len(parts) >= 3:
            _, message = alias_manager.remove_alias(parts[2])
            return message
        
        elif subcommand == "clear":
            _,message=alias_manager.clear_all_alias()
            return message
        
        elif subcommand == "list":
            if len(parts) >= 3:
                alias = alias_manager.list_aliases(parts[2])
                if alias:
                    return f"{parts[2]}: {alias['command']}\nDescription: {alias.get('description', '')}"
                return f"{format_text('red')}Invalid alias name: Alias not found{reset_format()}"
            aliases = alias_manager.list_aliases()
            return "\n".join([f"{name}: {data['command']} ,Description: {data['description'] if data['description'] else '-'}" for name, data in aliases.items()])
        
        elif subcommand == "import" and len(parts) >= 3:
            _, message = alias_manager.import_aliases(parts[2])
            return message
        
        elif subcommand == "export" and len(parts) >= 3:
            _, message = alias_manager.export_aliases(parts[2])
            return message
        
        elif subcommand == "help":
            return (
                "Alias Management Commands:\n"
                "  alias add <name> \"<command>\" --desc \"<description>\"- Add new alias\n"
                "  alias remove <name> - Remove alias\n"
                "  alias list [name] - List all aliases or show details\n"
                "  alias import <file> - Import aliases from JSON file\n"
                "  alias export <file> - Export aliases to JSON file\n"
                "  alias help - Show this help\n"
                "  alias clear - Clear all aliases"
            )
        
        return f"{format_text('red')}Invalid alias command: Use alias help for valid all commands{reset_format()}"
    except Exception as e:
        return f"{format_text('red')}Error processing alias command: {str(e)}{reset_format()}"