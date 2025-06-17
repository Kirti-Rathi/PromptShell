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

            if user_input.lower() in  ('quit', 'exit'):
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
                col_width = 18 
                print(f"""
{format_text('yellow', bold=True)}[Usage Patterns]{reset_format()}
  {format_text('cyan')}Natural Language:{reset_format()}  show me all python files modified last week
  {format_text('cyan')}Direct Execution:{reset_format()}  Use ! in input. eg., !ls -l
  {format_text('cyan')}Ask a Question:{reset_format()}    Use ? in input. eg., what is the purpose of the chmod command?

{format_text('yellow', bold=True)}[Special Commands]{reset_format()}
  {format_text('green')}{'--help':<{col_width}}{reset_format()}Show this help message
  {format_text('green')}{'--config':<{col_width}}{reset_format()}Re-run the setup wizard to change AI provider or model
  {format_text('green')}{'alias':<{col_width}}{reset_format()}Manage command shortcuts (use 'alias help' for details)
  {format_text('green')}{'clear / cls':<{col_width}}{reset_format()}Clear the terminal screen
  {format_text('green')}{'exit / quit':<{col_width}}{reset_format()}Terminate the assistant

{format_text('yellow', bold=True)}[Tips]{reset_format()}
  - Use {format_text('magenta')}Tab{reset_format()} for auto-completion of file and directory paths.
  - Prefixing with {format_text('magenta')}!{reset_format()} bypasses the AI for raw speed and direct execution.
""")
                continue

            if user_input.lower().rstrip().startswith("alias"):
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