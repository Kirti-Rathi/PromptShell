import sys
import glob
import os

def setup_readline():
    """Configures tab completion and history support."""
    
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
                        return prompt(">>> ", completer=PathCompleter())

                    print("Using prompt_toolkit for tab completion.")
                    return complete_path  # Return prompt-based tab completion
                except ImportError:
                    print("Warning: No readline or pyreadline3 found. Tab completion will not work.")
                    return

    # Configure readline for tab completion
    readline.parse_and_bind("tab: complete")

    def complete(text, state):
        matches = glob.glob(os.path.expanduser(text) + "*") + [None]
        return matches[state]

    readline.set_completer(complete)
    readline.set_completer_delims(" \t\n;")