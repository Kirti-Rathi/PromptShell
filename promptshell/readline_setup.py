import sys
import os
import atexit
import glob
import platform

# Define internal commands for tab completion
INTERNAL_COMMANDS = [
    '--help', '--config', '--tutorial', 
    'alias', 'exit', 'quit', 'clear', 'cls'
]

def clear_screen():
    """Clear the screen using ANSI escape sequences."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def setup_readline():
    """Configures tab completion, history support, and keyboard shortcuts."""
    histfile = os.path.join(os.path.expanduser("~"), ".promptshell_history")
    custom_prompt = None
    
    try:
        # Unix-like systems
        import readline
        
        # Load existing history
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            open(histfile, 'a').close()
        
        # Set history length and save on exit
        readline.set_history_length(1000)
        atexit.register(readline.write_history_file, histfile)
        
        # Configure tab completion
        readline.set_completer(completer)
        readline.set_completer_delims(" \t\n;")
        readline.parse_and_bind("tab: complete")
        
        # Bind Ctrl+L to clear screen
        readline.parse_and_bind("Control-l: clear_screen")
        print("Using readline for enhanced input features.")
        
    except ImportError:
        if sys.platform == "win32":
            try:
                # Windows with pyreadline
                import pyreadline3 as readline
                
                # Load existing history
                try:
                    readline.read_history_file(histfile)
                except FileNotFoundError:
                    open(histfile, 'a').close()
                
                # Set history length and save on exit
                readline.set_history_length(1000)
                atexit.register(readline.write_history_file, histfile)
                
                # Configure tab completion
                readline.set_completer(completer)
                readline.parse_and_bind("tab: complete")
                
                # Bind Ctrl+L to clear screen
                readline.parse_and_bind("Control-l: clear_screen")
                print("Using pyreadline for enhanced input features.")
                
            except ImportError:
                # Fallback to prompt_toolkit
                try:
                    import prompt_toolkit
                    from prompt_toolkit.completion import Completer, Completion
                    from prompt_toolkit.shortcuts import prompt as pt_prompt
                    from prompt_toolkit.keys import Keys
                    from prompt_toolkit.key_binding import KeyBindings
                    from prompt_toolkit.history import FileHistory
                    
                    print("Using prompt_toolkit for enhanced input features.")
                    
                    # Set up history
                    history = FileHistory(histfile)
                    
                    # Custom completer class
                    class InternalCompleter(Completer):
                        def get_completions(self, document, complete_event):
                            text = document.text_before_cursor
                            # Internal commands
                            for cmd in INTERNAL_COMMANDS:
                                if cmd.startswith(text):
                                    yield Completion(cmd, start_position=-len(text))
                            # File paths
                            for path in glob.glob(os.path.expanduser(text) + "*"):
                                yield Completion(path, start_position=-len(text))
                    
                    # Key bindings for clear screen (Ctrl+L)
                    bindings = KeyBindings()
                    
                    @bindings.add(Keys.ControlL)
                    def clear_screen(event):
                        event.app.renderer.clear()
                    
                    def custom_prompt(prompt_str):
                        return pt_prompt(
                            prompt_str,
                            history=history,
                            completer=InternalCompleter(),
                            key_bindings=bindings
                        )
                    
                    return custom_prompt
                    
                except ImportError:
                    print("Warning: No readline or pyreadline3 found. Tab completion will not work.")
        else:
            print("Warning: readline not available. Tab completion will not work.")
    
    return custom_prompt

def completer(text, state):
    """Tab completion function that completes both internal commands and file paths."""
    # First check internal commands
    command_matches = [cmd for cmd in INTERNAL_COMMANDS if cmd.startswith(text)]
    
    # Then check file paths
    file_matches = glob.glob(os.path.expanduser(text) + "*")
    
    # Combine both types of matches
    matches = command_matches + file_matches
    return matches[state] if state < len(matches) else None