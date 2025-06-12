import pyperclip
import subprocess

class DataGatherer:
    @staticmethod
    def get_clipboard_content():
        """Retrieves the current content of the clipboard.

        Returns:
            str: The content of the clipboard or an error message if unable to access it.
        """
        try:
            return pyperclip.paste()
        except:
            return "Error: Unable to access clipboard"

    @staticmethod
    def get_file_content(file_path):
        """Reads the content of a specified file.

        Args:
            file_path (str): The path to the file to read.

        Returns:
            str: The content of the file or an error message if reading fails.
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def execute_command(command):
        """Executes a shell command and captures its output.

        Args:
            command (str): The shell command to execute.

        Returns:
            str: The standard output of the command or an error message if execution fails.
        """
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
        except Exception as e:
            return f"Error executing command: {str(e)}"