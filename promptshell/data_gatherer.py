import pyperclip
import subprocess

class DataGatherer:
    @staticmethod
    def get_clipboard_content():
        """Gets current clipboard content.
        
        Returns:
            Clipboard text or error message
        """

        try:
            return pyperclip.paste()
        except:
            return "Error: Unable to access clipboard"

    @staticmethod
    def get_file_content(file_path):
        """Reads file contents.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content or error message
        """

        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def execute_command(command):
        """Executes command and returns output.
        
        Args:
            command: Command to execute
            
        Returns:
            Command output or error message
        """
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error executing command: {str(e)}"