import pyperclip
import subprocess

class DataGatherer:
    """
    A utility class for gathering different types of input data:
    clipboard content, file content, and shell command output.
    """
    @staticmethod
    def get_clipboard_content():
        """
        Retrieve the current text content from the system clipboard.

        Returns:
            str: Clipboard content if successful, or an error message if not.
        """
        try:
            return pyperclip.paste()
        except:
            return "Error: Unable to access clipboard"

    @staticmethod
    def get_file_content(file_path):
        """
        Read and return the content of a specified file.

        Args:
            file_path (str): Path to the file to be read.

        Returns:
            str: File content if successful, or an error message if the file couldn't be read.
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def execute_command(command):
        """
        Execute a shell command and return its output.

        Args:
            command (str): The shell command to execute.

        Returns:
            str: Standard output if successful, or the error message if the command fails.
        """
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error executing command: {str(e)}"