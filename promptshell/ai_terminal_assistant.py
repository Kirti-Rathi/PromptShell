import os
import subprocess
import shlex
import getpass
import sys
import platform
import questionary
from typing import Tuple
from .node import Node
from .data_gatherer import DataGatherer
from .format_utils import format_text, reset_format
from .system_info import get_system_info

def get_current_os():
    return platform.system()

class AITerminalAssistant:
    def __init__(self, model_name: str, max_tokens: int = 8000, config: dict = None):
        self.username = getpass.getuser()
        self.home_folder = os.path.expanduser("~")
        self.current_directory = os.getcwd()
        self.config = config or {}

        self.command_executor = Node(model_name, "Command Executor", max_tokens=max_tokens, config=self.config)
        self.error_handler = Node(model_name, "Error Handler", max_tokens=max_tokens, config=self.config)
        self.debugger = Node(model_name, "Debugger Expert", max_tokens=max_tokens, config=self.config)
        self.question_answerer = Node(model_name, "Question Answerer", max_tokens=max_tokens, config=self.config)
        self.data_gatherer = DataGatherer()
        self.command_history = []

        self.initialize_system_context()

    def initialize_system_context(self):
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        installed_commands = []
        for dir in path_dirs:
            if os.path.isdir(dir):
                try:
                    installed_commands.extend([f for f in os.listdir(dir) if os.access(os.path.join(dir, f), os.X_OK)])
                except PermissionError:
                    continue
        installed_commands = list(set(installed_commands))
        
        try:
            system_info = get_system_info()
        except Exception:
            system_info = "Unable to retrieve system information"

        self.command_executor.definition = f"""
        [ROLE] Shell Command Interpreter
        [TASK] Translate natural language requests into precise shell commands
        
        [CONTEXT]
        User: {self.username}
        Shell: {os.environ.get('SHELL', 'Unknown')}
        OS: {system_info.get('os', 'Unknown')} {system_info.get('release', '')}
        CPU: {system_info.get('cpu', 'Unknown')}
        Architecture: {system_info.get('machine', 'Unknown')}
        Platform: {system_info.get('platform', 'Unknown')}
        Path: {self.current_directory}
        Installations: {', '.join(installed_commands[:75])}
        
        [GUIDELINES]
        1. Output ONLY valid shell commands - no explanations
        2. Prefer built-in tools over external dependencies
        3. Security priority: Add 'CONFIRM:' prefix for:
        - File deletion (rm, del)
        - System modifications (chmod, format)
        - Network operations (ssh, scp)
        - Package management (apt, yum)
        4. OS-specific patterns:
        Windows: Use 'dir', 'where', 'tasklist'
        Unix: Use 'ls', 'which', 'ps'
        5. Handle spaces in paths with proper quoting
        6. For multi-step operations, use && or ;
        
        [SAFETY PROTOCOLS]
        - Never suggest commands that could damage system
        - Reject unsafe requests with: "SafetyError: [reason]"
        - Validate file existence before operations
        - Prefer read-only alternatives first
        
        [EXAMPLES]
        User: List large PDFs
        CMD: find . -name "*.pdf" -size +5M
        User: Search config for 'timeout'
        CMD: grep -rnw './' -e 'timeout'
        """

        self.error_handler.definition = f"""
        [ROLE] Command Error Diagnostician
        [TASK] Analyze failed commands and suggest fixes
        
        [ANALYSIS FRAMEWORK]
        1. Check path resolution
        2. Verify command exists in {path_dirs}
        3. Validate file/directory permissions
        4. Check argument syntax
        5. Look for typos or similar valid commands
        
        [OUTPUT FORMAT]
        [Error Type]: Brief description
        [Solution]: Single corrected command
        [Alternative]: Safer alternative if available
        
        [EXAMPLES]
        Error: 'rm: missing operand'
        Solution: Confirm file existence with 'ls'
        Alternative: Use trash-cli instead of rm
        """
        
        self.debugger.definition = f"""
        [ROLE] Shell Environment Debugger
        [TASK] Diagnose complex system issues
        
        [DIAGNOSTIC TOOLS]
        - Check environment variables
        - Verify service statuses
        - Analyze process tree
        - Review recent system changes
        - Test network connectivity
        
        [OUTPUT STRUCTURE]
        1. Identified Issue
        2. Confidence Level (High/Med/Low)
        3. Immediate Fix
        4. Long-term Solution
        5. Verification Command
        
        [EXAMPLE]
        Issue: Missing PATH entry
        Fix: export PATH=$PATH:/missing/path
        Verify: echo $PATH | grep '/missing/path'
        """

        self.question_answerer.definition = f"""
        [ROLE] Technical Knowledge Engineer
        [TASK] Provide accurate, context-aware answers
        
        [RESPONSE GUIDELINES]
        1. Start with direct answer
        2. Add OS-specific notes
        3. Include basic example
        4. Mention alternatives
        5. Add safety considerations
        
        [CONTEXT AWARENESS]
        - Current directory: {self.current_directory}
        - Recent commands: {self.command_history[-3:]}
        - System resources: {system_info.get('memory', 'Unknown')}
        
        [EXAMPLE]
        Question: Monitor CPU usage?
        Answer: Use 'top' (Linux) or 'perfmon' (Win)
        Linux Example: 'top -o %CPU'
        Windows Example: 'perfmon /res'
        """

    def execute_command_with_live_output(self, command: str) -> Tuple[str, str, int]:
        interactive_commands = [
            'vim', 'vi', 'nano', 'emacs', 'ssh', 'telnet', 'top', 'htop',
            'man', 'less', 'more', 'mysql', 'psql', 'nmtui', 'crontab',
            'passwd', 'sudo', 'su', 'gdb', 'screen', 'tmux', 'nano', 'picocom',
            'powershell', 'cmd', 'ftp', 'sftp', 'taskmgr', 'notepad', 'regedit'
        ]
        is_interactive = any(command.strip().startswith(cmd) for cmd in interactive_commands)
        if is_interactive:
            return self.execute_interactive_command(command)

        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(command, shell=True, text=True, capture_output=True)
                print(result.stdout)
                if result.stderr:
                    print(format_text('red') + "Error: " + result.stderr + reset_format())
                return result.stdout, result.stderr, result.returncode
            else:
                args = shlex.split(command)
                result = subprocess.run(args, text=True, capture_output=True)
                print(result.stdout)
                if result.stderr:
                    print(format_text('red') + "Error: " + result.stderr + reset_format())
                return result.stdout, result.stderr, result.returncode
        except Exception as e:
            print(format_text('red') + f"Execution error: {e}" + reset_format())
            return "", str(e), 1

    def execute_interactive_command(self, command: str) -> Tuple[str, str, int]:
        print(format_text('yellow') + "Executing interactive command..." + reset_format())
        try:
            proc = subprocess.Popen(
                shlex.split(command),
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True
            )
            proc.communicate()
            if proc.returncode != 0:
                print(format_text('red') + f"Command exited with code {proc.returncode}" + reset_format())
            return "", "", proc.returncode
        except Exception as e:
            print(format_text('red') + f"Execution failed: {str(e)}" + reset_format())
            return "", str(e), 1

    def execute_command(self, user_input: str) -> str:
        try:
            command = None  # Initialize command variable
            self.current_directory = os.getcwd()
            
            # Basic input validation
            if user_input.strip() == "":
                return "Please provide a valid input."
                
            if user_input.startswith('?') or user_input.endswith('?'):
                return self.answer_question(user_input)
            if user_input.lower().strip() == 'clear' or user_input.lower().strip() == 'cls':
                if get_current_os() == 'windows':
                    os.system('cls')
                else:
                    os.system('clear')
                return ""
            if user_input.startswith('!'):
                return self.run_direct_command(user_input[1:])
            additional_data = self.gather_additional_data(user_input)
            command = self.command_executor(f"""
            User Input: {user_input}
            Current OS: {platform.system()}
            Current Directory: {self.current_directory}
            Translate the user input into a SINGLE shell command.
            Return ONLY the command, nothing else.
            """, additional_data=additional_data).strip()

            # Handle dangerous commands with two-step verification
            if self.is_dangerous_command(command):
                # First confirmation
                proceed = input(format_text('yellow', bold=True) + 
                    f"\n⚠️  Warning: This is a destructive command.\nDo you want to continue? (yes/no): " + 
                    reset_format())
                if proceed.strip().lower() != "yes":
                    return format_text('red', bold=True) + "\nCommand aborted by user." + reset_format()

                # Second confirmation - manual reentry
                confirm_input = input(format_text('yellow', bold=True) + 
                    f"For safety, please re-type the exact command to proceed:\n> " + 
                    reset_format())
                if confirm_input.strip() != command.strip():
                    return format_text('red', bold=True) + "\n❌ Command mismatch. Operation aborted!" + reset_format()

            # Execute the validated command
            return self._execute_validated_command(command)

        except Exception as e:
            print(format_text('red') + f"Error: {str(e)}" + reset_format())
            return format_text('red') + "Command execution failed." + reset_format()

    def handle_error(self, error: str, user_input: str, command: str) -> str:
        try:
            error_analysis = self.error_handler(f"""
            Error: {error}
            User Input: {user_input}
            Interpreted Command: {command}
            Current Directory: {self.current_directory}
            Provide ONLY a single, simple corrected command. No explanations.
            """)
            
            print(format_text('red') + f"Error occurred: {error}" + reset_format())
            print(format_text('yellow') + f"Suggested command: {error_analysis}" + reset_format())
            
            if questionary.confirm("Would you like to execute the suggested command?").ask():
                return self._execute_validated_command(error_analysis)
            return format_text('red') + "Command execution aborted." + reset_format()

        except Exception as e:
            return format_text('red') + f"Error handler failed: {str(e)}" + reset_format()

    def _execute_validated_command(self, command: str) -> str:
        """Helper method to execute validated commands"""
        if command.startswith("cd "):
            path = command.split(" ", 1)[1]
            os.chdir(os.path.expanduser(path))
            return f"Changed directory to {os.getcwd()}"
            
        stdout, stderr, exit_code = self.execute_command_with_live_output(command)
        if exit_code != 0 and stderr:
            debug_suggestion = self.debug_error(command, stderr, exit_code)
            return format_text('yellow') + f"\nDebugging Suggestion:\n{debug_suggestion}" + reset_format()
        
        return stdout.strip() if stdout else ""

    def run_direct_command(self, command: str) -> str:
        try:
            formatted_command = format_text('cyan') + f"Direct Command: {command}" + reset_format()
            print(formatted_command)
            self.command_history.append(command)
            if len(self.command_history) > 10:
                self.command_history.pop(0)
            if command.startswith("cd "):
                path = command.split(" ", 1)[1]
                os.chdir(os.path.expanduser(path))
                return f"Changed directory to {os.getcwd()}"
            if command.lower().strip() == 'clear' or command.lower().strip() == 'cls':
                if get_current_os() == 'windows':
                    os.system('cls')
                else:
                    os.system('clear')
                return ""
            else:
                stdout, stderr, exit_code = self.execute_command_with_live_output(command)
                result = ""
                if exit_code != 0:
                    debug_suggestion = self.debug_error(command, stderr, exit_code)
                    result += format_text('yellow') + f"\n\nDebugging Suggestion:\n{debug_suggestion}" + reset_format()
                return result.strip()
        except Exception as e:
            return self.handle_error(str(e), command, command)

    def answer_question(self, question: str) -> str:
        context = f"""
        Command History (last 10 commands):
        {', '.join(self.command_history)}
        Current Directory: {self.current_directory}
        """
        answer = self.question_answerer(f"""
        Question: {question.strip('?')}
        Context:
        {context}
        Please provide a clear and concise answer to the question, taking into account the given context.
        """)
        return format_text('cyan') + "Answer:\n" + answer + reset_format()

    def gather_additional_data(self, user_input: str) -> dict:
        additional_data = {}
        if "clipboard" in user_input.lower():
            clipboard_content = self.data_gatherer.get_clipboard_content()
            additional_data["clipboard_content"] = clipboard_content
        file_keywords = ["file", "content", "read", "merge"]
        if any(keyword in user_input.lower() for keyword in file_keywords):
            words = user_input.split()
            for word in words:
                if os.path.isfile(word):
                    with open(word, 'r') as file:
                        file_content = file.read()
                    additional_data["file_content"] = file_content
                    additional_data["target_file"] = word
                    break
        return additional_data

    def debug_error(self, command: str, error_output: str, exit_code: int) -> str:
        context = f"""
        Command History (last 10 commands):
        {', '.join(self.command_history)}
        Current Directory: {self.current_directory}
        Last Command: {command}
        Error Output: {error_output}
        Exit Code: {exit_code}
        """
        debug_input = f"""
        Analyze the following command and its error output.
        Provide a brief explanation of what went wrong and suggest a solution or alternative approach.
        Keep your response concise and focused on solving the immediate issue.
        {context}
        """
        return self.debugger(debug_input)

    def is_dangerous_command(self, command: str) -> bool:
        dangerous_keywords = [
            "rm ", "rmdir ", "del ", "delete ",  # File deletion
            "chmod ", "chown ", "attrib ",       # Permission changes
            "mkfs.", "format ",                  # Formatting
            "dd ",                               # Direct disk operations
            "mv ", "move ",                      # Moving files
            "> ",                                # Output redirection that might overwrite
            "reboot", "shutdown",                # System commands
            "init 0", "init 6"                   # System state changes
        ]
        return any(command.strip().lower().startswith(kw.lower()) for kw in dangerous_keywords)