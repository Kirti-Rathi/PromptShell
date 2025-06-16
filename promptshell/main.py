"""
Main entry point for the AI-Powered Terminal Assistant.

This module initializes configuration, sets up terminal features, and
launches a continuous input loop where user queries are processed
either as shell commands or natural language queries via an AI assistant.
"""

from .ai_terminal_assistant import AITerminalAssistant
from .readline_setup import setup_readline
import platform
import os
from .ansi_support import enable_ansi_support
from .format_utils import format_text, reset_format, get_terminal_size
from .setup import setup_wizard, load_config, get_active_model
from .alias_manager import handle_alias_command

def main():
    """
    Initialize and run the terminal assistant.

    - Loads user configuration or starts setup if none exists.
    - Enables ANSI support and readline for better UX.
    - Loads the AI model and enters an input loop.
    - Supports:
        - Shell command execution
        - Natural language queries
        - Aliases
        - Help/config handling
        - Graceful termination on 'quit' or keyboard interrupt.
    """
    config = load_config()
    if not config:
        print("First-time setup required!")
        setup_wizard()
        config = load_config()

    enable_ansi_support()
    setup_readline()
    model_name = get_active_model()

    assistant = AITerminalAssistant(config=config, model_name=model_name)

    print(f"""\n{format_text('green', bold=True)}Welcome to the AI-Powered Terminal Assistant!
Active provider: ({model_name} - {platform.system()})
Type '--help' for assistance and '--config' for settings.{reset_format()}""")
    
    while True:
        try:
            columns, _ = get_terminal_size()
            prompt = f"\n{format_text('green', bold=True)}{os.getcwd()}$ {reset_format()}"
            user_input = input(prompt)

            if len(prompt) + len(user_input) > columns:
                print()  # Move to the next line if input is too long

            if user_input.lower() == 'quit':
                print(format_text('red', bold=True) + "\nTerminating..." + reset_format())
                break

            if user_input.lower() == "--config":
                setup_wizard()
                config = load_config()
                model_name = get_active_model()
                assistant = AITerminalAssistant(config=config, model_name=model_name)
                print(f"{format_text('yellow', bold=True)}Configuration updated!{reset_format()}")
                continue

            if user_input.lower() == "--help":
                print(f"""{format_text('blue')}- You can use natural language queries or standard shell commands.
- Start your input with '!' to execute a command directly without processing.
- Start or end your input with '?' to ask a question.
- Tab completion for files and folders is enabled.
- Use 'Ctrl + c' or type 'quit' to quit the assistant.
- Type 'clear' to clear the terminal.{reset_format()}""")
                continue

            if user_input.lower().startswith("alias "):
                result = handle_alias_command(user_input, assistant.alias_manager)
                print(result)
                continue

            result = assistant.execute_command(user_input)
            print(result)

        except KeyboardInterrupt:
            print(format_text('red', bold=True) + "\nTerminating..." + reset_format())
            break

if __name__ == "__main__":
    main()
