import sys
import glob
import os

def setup_readline():
    """
    Sets up tab completion support for the command-line interface.

    On Unix-like systems, it attempts to use the built-in `readline` module.
    On Windows, it tries to use `pyreadline3`, and if not available, falls back to 
    `prompt_toolkit` for enhanced input handling with tab-completion.

    If none of these options are available, it disables tab completion and prints a warning.

    Returns:
        function or None: If `prompt_toolkit` is used, returns a prompt function with path completion.
                          Otherwise, returns None.
    """
    try:
        import readline  # Works on Unix-like systems
    except ImportError:
        if sys.platform == "win32":
            try:
                import pyreadline3 as readline  # Use pyreadline3 on Windows
            except ImportError:
                try:
                    import prompt_toolkit  # Alternative for better Windows support
                    from prompt_toolkit.completion import PathCompleter
                    from prompt_toolkit.shortcuts import prompt

                    def complete_path():
                        """
                        Prompt user input with file path autocompletion using prompt_toolkit.

                        Returns:
                            str: User input string with path completion.
                        """
                        return prompt(">>> ", completer=PathCompleter())

                    print("Using prompt_toolkit for tab completion.")
                    return complete_path  # Return prompt-based tab completion
                except ImportError:
                    print("Warning: No readline or pyreadline3 found. Tab completion will not work.")
                    return

    # Configure readline for tab completion
    readline.parse_and_bind("tab: complete")

    def complete(text, state):
        """
        Completer function for readline. Matches file paths based on current input.

        Args:
            text (str): The current input text to complete.
            state (int): The state of the completion (0 for first match, 1 for next, etc.)

        Returns:
            str or None: The matching completion or None if no more matches.
        """
        matches = glob.glob(os.path.expanduser(text) + "*") + [None]
        return matches[state]

    readline.set_completer(complete)
    readline.set_completer_delims(" \t\n;")
