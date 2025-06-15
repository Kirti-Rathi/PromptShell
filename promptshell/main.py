from .ai_terminal_assistant import AITerminalAssistant
from .readline_setup import setup_readline
import platform
import os
from .ansi_support import enable_ansi_support
from .format_utils import format_text, reset_format, get_terminal_size
from .setup import setup_wizard, load_config, get_active_model
from .alias_manager import handle_alias_command

def main():
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
-Use 'Ctrl + c' or type 'quit' to exit the assistant.
- Type 'clear' to clear the terminal.{reset_format()}""")
                continue

        continue

        # ✅ Check for destructive command
        if user_input.startswith("CONFIRM:"):
            actual_command = user_input.replace("CONFIRM:", "", 1).strip()

            # Step 1: Initial yes/no confirmation
            proceed = input(format_text('yellow', bold=True) + f"\n⚠️  This is a destructive command.\nDo you want to continue? (yes/no): " + reset_format())
            if proceed.strip().lower() != "yes":
                print(format_text('red', bold=True) + "\nCommand aborted by user." + reset_format())
                continue

            # Step 2: Manual re-entry for safety
            confirm_input = input(format_text('yellow', bold=True) + f"Type the exact command to proceed:\n> " + reset_format())
            if confirm_input.strip() != actual_command:
                print(format_text('red', bold=True) + "\n❌ Mismatch. Aborting execution!" + reset_format())
                continue

            # If matched, allow execution
            user_input = actual_command

        # ✅ Handle alias command
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