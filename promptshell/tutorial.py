import os
import sys
from typing import Dict, List, Optional, Callable
import questionary
import time # Import time for sleep
from .format_utils import format_text, reset_format
from .setup import CONFIG_DIR

TUTORIAL_PROGRESS_FILE = os.path.join(CONFIG_DIR, "tutorial_progress.json")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class TutorialStep:
    def __init__(self, title: str, content: str, exercise: Optional[str] = None, 
                 validation: Optional[Callable[[str], bool]] = None, hints: Optional[List[str]] = None, 
                 simulated_output: Optional[str] = None, dynamic_output_generator: Optional[Callable[[str], str]] = None):
        self.title = title
        self.content = content
        self.exercise = exercise
        self.validation = validation
        self.hints = hints or []
        self.simulated_output = simulated_output
        self.dynamic_output_generator = dynamic_output_generator

class Tutorial:
    def __init__(self):
        self.steps = [
            TutorialStep(
                "Welcome to PromptShell!",
                f"""Welcome to the interactive tutorial for PromptShell! This tutorial will guide you through the core features and help you get started.

{format_text('green', bold=True)}What is PromptShell?{reset_format()}
PromptShell is an AI-powered terminal assistant that helps you interact with your system using natural language. It combines the power of AI with traditional shell commands to make your terminal experience more intuitive and efficient.

{format_text('yellow', bold=True)}Tutorial Navigation:{reset_format()}
{format_text('cyan', bold=True)}Basic Navigation:{reset_format()}
  next/n     - Go to next step
  prev/p     - Go to previous step
  skip/s     - Skip current step
  exit/q     - Quit tutorial
  help/h     - Show help menu
  hint       - Get a hint for current exercise

{format_text('cyan', bold=True)}Advanced Navigation:{reset_format()}
  goto <n>   - Jump to step number n
  list/ls    - List all available steps
  reset      - Start tutorial from beginning
  save       - Save current progress
  load       - Load last saved progress

{format_text('cyan', bold=True)}Exercise Commands:{reset_format()}
  try        - Try the current exercise
  skip       - Skip current exercise
  hint       - Get a hint for the exercise

Let's begin! Type 'next' or press Enter to continue...""",
                hints=["Type 'help' anytime for navigation commands", "Type 'hint' when you're stuck on an exercise"]
            ),
            TutorialStep(
                "Natural Language Commands",
                f"""{format_text('green', bold=True)}Natural Language Commands{reset_format()}
One of PromptShell's most powerful features is the ability to execute commands using natural language. Instead of remembering complex command syntax, you can simply describe what you want to do.

{format_text('yellow', bold=True)}Example:{reset_format()}
Instead of: !find . -name "*.txt" -type f -mtime -7
You can type: show me all text files modified in the last week

{format_text('cyan', bold=True)}Try it yourself:{reset_format()}
Type: list all files in the current directory

{format_text('magenta', bold=True)}Note:{reset_format()}
- Be specific in your requests
- Use natural language as you would speak
- The AI will translate your request into the appropriate shell command""",
                exercise="Try listing all files in the current directory using natural language",
                validation=lambda x: "list" in x.lower() and "file" in x.lower(),
                hints=["Try using words like 'list', 'show', or 'display'", "Mention that you want to see 'files' or 'contents'"],
                dynamic_output_generator=lambda x: (
                    "Understood! Simulating a list of files based on your request: \n.DS_Store\npromptshell/\nREADME.md\ntests/\n.gitignore\nLICENSE\npyproject.toml" if "list all files in the current directory" in x.lower() else
                    f"Understood! Simulating response for: {x.strip()}\n.DS_Store\npromptshell/\nREADME.md\ntests/\n.gitignore\nLICENSE\npyproject.toml" # Generic fallback
                )
            ),
            TutorialStep(
                "Direct Command Execution",
                f"""{format_text('green', bold=True)}Direct Command Execution{reset_format()}
Sometimes you want to execute shell commands directly without AI processing. PromptShell makes this easy with the '!' prefix.

{format_text('yellow', bold=True)}Example:{reset_format()}
!ls -la
!pwd
!echo "Hello World"

{format_text('cyan', bold=True)}Try it yourself:{reset_format()}
Type: !echo "Welcome to PromptShell"

{format_text('magenta', bold=True)}Note:{reset_format()}
- The '!' prefix bypasses AI processing
- Commands are executed exactly as typed
- Useful for quick, simple commands""",
                exercise="Try printing a welcome message using direct command execution",
                validation=lambda x: x.startswith('!'),
                hints=["Start your command with '!'", "Try commands like !ls, !pwd, !echo, !mkdir, !rm"],
                dynamic_output_generator=lambda x: (
                    "Welcome to PromptShell" if x.lower() == '!echo "welcome to promptshell"' else
                    "Output for: " + x + "\n.DS_Store\npromptshell/\nREADME.md\ntests/\n.gitignore\nLICENSE\npyproject.toml" if 'ls' in x.lower() else
                    "Output for: " + x + "\n/c/Users/piyus/OneDrive/Desktop/SSOC/PromptShell" if 'pwd' in x.lower() else
                    "Output for: " + x + "\nDirectory created: " + x.split(' ', 1)[1] if 'mkdir' in x.lower() and len(x.split(' ', 1)) > 1 else
                    "Output for: " + x + "\nFile or directory removed: " + x.split(' ', 1)[1] if 'rm' in x.lower() and len(x.split(' ', 1)) > 1 else
                    x.split(' ', 1)[1].strip("\'\"") if 'echo' in x.lower() and len(x.split(' ', 1)) > 1 else
                    f"Executing: {x.strip()}" # Generic fallback
                )
            ),
            TutorialStep(
                "Asking Questions",
                f"""{format_text('green', bold=True)}Asking Questions{reset_format()}
Need help with a command or concept? Just ask! Use the '?' prefix or suffix to ask questions about shell commands, system operations, or general computing concepts.

{format_text('yellow', bold=True)}Example:{reset_format()}
What is the difference between 'cp' and 'mv'?
How do I create a new directory??
?What is the purpose of the chmod command?

{format_text('cyan', bold=True)}Try it yourself:{reset_format()}
Type: ?What is the purpose of the 'ls' command?

{format_text('magenta', bold=True)}Note:{reset_format()}
- Questions can be prefixed or suffixed with '?'
- The AI will provide clear, concise answers
- Great for learning new commands and concepts""",
                exercise="Try asking a question about a command using the ? prefix",
                validation=lambda x: x.startswith('?') or x.endswith('?'),
                hints=["Start or end your question with '?'", "Ask about a specific command's purpose"],
                dynamic_output_generator=lambda x: (
                    "The 'ls' command lists the contents of a directory. It shows files and subdirectories." if 'ls' in x.lower() else
                    "The 'mkdir' command creates new directories. You can specify the full path to the new directory." if 'create' in x.lower() and ('directory' in x.lower() or 'folder' in x.lower()) or 'mkdir' in x.lower() else
                    "The 'cp' command copies files or directories, while 'mv' moves (renames) them." if 'cp' in x.lower() and 'mv' in x.lower() and 'difference' in x.lower() else
                    "The 'chmod' command changes file permissions (read, write, execute) for users, groups, and others." if 'chmod' in x.lower() and 'purpose' in x.lower() else
                    "The 'cd' command changes the current working directory." if 'cd' in x.lower() else
                    "The 'pwd' command prints the name of the current working directory." if 'pwd' in x.lower() else
                    "The 'rm' command removes files or directories." if 'rm' in x.lower() else
                    "That's an interesting question! For this tutorial, we simulate a general response. Please try asking about a specific shell command to see a tailored simulated response."
                )
            ),
            TutorialStep(
                "Smart Tab Completion",
                f"""{format_text('green', bold=True)}Smart Tab Completion{reset_format()}
PromptShell includes intelligent tab completion for files and directories in your current working directory.

{format_text('yellow', bold=True)}How to use (in real PromptShell):{reset_format()}
1. Start typing a file or directory name
2. Press Tab to see matching options
3. Press Tab multiple times to cycle through options
4. Press Enter to select

{format_text('yellow', bold=True)}How to demonstrate in this tutorial:{reset_format()}
Type 'cd ' (with a space after cd) and press Enter to see simulated tab completion options.

{format_text('cyan', bold=True)}Try it yourself:{reset_format()}
Type: cd 
(Then press Enter to see a simulated list of directories)

{format_text('magenta', bold=True)}Note:{reset_format()}
- In a real PromptShell, you would press TAB for interactive completion
- This tutorial simulates the *output* of tab completion
- Works with both natural language and direct commands
- Helps prevent typos in file paths
- Saves time when navigating directories""",
                exercise="Try using tab completion to navigate to a directory",
                validation=lambda x: x.startswith('cd '),
                hints=["Type 'cd ' and press Enter", "The tutorial will show you the simulated completion options"],
                dynamic_output_generator=lambda x: f"""{format_text('yellow', bold=True)}Available directories:{reset_format()}
  {format_text('cyan')}promptshell/{reset_format()}    - Main package directory
  {format_text('cyan')}tests/{reset_format()}         - Test files
  {format_text('cyan')}docs/{reset_format()}          - Documentation
  {format_text('cyan')}examples/{reset_format()}      - Example scripts
  {format_text('cyan')}venv/{reset_format()}          - Virtual environment

{format_text('green')}Tip: Use arrow keys or type more characters to filter results{reset_format()}"""
            ),
            TutorialStep(
                "User-Defined Aliases",
                f"""{format_text('green', bold=True)}User-Defined Aliases{reset_format()}
Create shortcuts for frequently used commands using the alias system.

{format_text('yellow', bold=True)}Basic Alias Commands:{reset_format()}
- alias add <name> \"<command>\" --desc \"description\"- Create new alias
- alias list - Show all aliases
- alias list <name> - Show details about an alias
- alias remove <name> - Remove an alias
- alias import/export <file> - Import/export aliases

{format_text('cyan', bold=True)}Try it yourself:{reset_format()}
1. First create the alias:
   Type: alias add hello \"echo 'Hello, World!'\""

2. Then execute the alias:
   Type: !hello

{format_text('magenta', bold=True)}Note:{reset_format()}
- Aliases can include complex commands
- Use quotes for commands with spaces
- Aliases persist between sessions
- Use ! prefix to execute aliases""",
                exercise="Try creating an alias for a simple command",
                validation=lambda x: x.startswith('alias add ') or x == '!hello',
                hints=["First type 'alias add hello' to create the alias", "Then type '!hello' to execute it"],
                dynamic_output_generator=lambda x: (
                    f"Alias '{x.split(' ')[2]}' added successfully." if x.startswith('alias add') and len(x.split(' ')) > 2
                    else "Hello, World!" if x == '!hello'
                    else "Alias added successfully.")
            ),
            TutorialStep(
                "Congratulations!",
                f"""{format_text('green', bold=True)}Congratulations!{reset_format()}
You've completed the PromptShell tutorial! You now know how to:
- Use natural language commands
- Execute direct shell commands

{format_text('yellow', bold=True)}Remember:{reset_format()}
- Type --help anytime for a quick reference
- Use --config to change settings
- Type 'exit' or 'quit' to close PromptShell

{format_text('cyan', bold=True)}Happy coding!{reset_format()}"""
            )
        ]
        self.current_step = 0  # Always start from the beginning
        # Remove loading of saved progress since we want to start fresh each time
        # self.load_progress()
        self.current_hint_index: Dict[int, int] = {}

    def load_progress(self):
        """Load progress from file. Only used when explicitly requested via 'load' command."""
        if os.path.exists(TUTORIAL_PROGRESS_FILE):
            try:
                with open(TUTORIAL_PROGRESS_FILE, 'r') as f:
                    self.current_step = int(f.read().strip())
            except Exception:
                self.current_step = 0

    def save_progress(self):
        """Save progress to file. Only used when explicitly requested via 'save' command."""
        with open(TUTORIAL_PROGRESS_FILE, 'w') as f:
            f.write(str(self.current_step))

    def reset_progress(self):
        """Reset progress to beginning."""
        self.current_step = 0
        self.save_progress()

    def show_help(self):
        print(f"""
{format_text('yellow', bold=True)}Tutorial Help{reset_format()}

{format_text('cyan', bold=True)}Basic Navigation:{reset_format()}
  next/n     - Go to next step
  prev/p     - Go to previous step
  skip/s     - Skip current step
  exit/q     - Quit tutorial
  help/h     - Show this help message
  hint       - Get a hint for current exercise

{format_text('cyan', bold=True)}Advanced Navigation:{reset_format()}
  goto <n>   - Jump to step number n
  list/ls    - List all available steps
  reset      - Start tutorial from beginning
  save       - Save current progress
  load       - Load last saved progress

{format_text('cyan', bold=True)}Exercise Commands:{reset_format()}
  try        - Try the current exercise
  skip       - Skip current exercise
  hint       - Get a hint for the exercise

{format_text('yellow', bold=True)}Progress:{reset_format()}
  - Progress is saved only when you use the 'save' command
  - Use 'load' to resume from a saved point
  - Type 'reset' to start over
  - Tutorial always starts from beginning when launched

{format_text('yellow', bold=True)}Tips:{reset_format()}
  - Read the examples carefully
  - Try the exercises
  - Use hints if you're stuck
  - Take your time to understand each feature
""")

    def show_hint(self):
        step = self.steps[self.current_step]
        if step.hints:
            # Get current hint index for this step, default to 0
            current_hint_idx = self.current_hint_index.get(self.current_step, 0)
            
            print(f"\n{format_text('cyan', bold=True)}Hint {current_hint_idx + 1}/{len(step.hints)}:{reset_format()}")
            print(step.hints[current_hint_idx])
            
            # Increment hint index, cycle back to 0 if overflow
            self.current_hint_index[self.current_step] = (current_hint_idx + 1) % len(step.hints)
        else:
            print(f"\n{format_text('yellow')}No hints available for this step.{reset_format()}")

    def list_steps(self):
        print(f"\n{format_text('yellow', bold=True)}Available Steps:{reset_format()}")
        for i, step in enumerate(self.steps):
            current = " → " if i == self.current_step else "   "
            print(f"{current}{i+1}. {step.title}")

    def goto_step(self, step_num: int):
        if 1 <= step_num <= len(self.steps):
            self.current_step = step_num - 1
            self.save_progress()
            return True
        return False

    def handle_navigation(self, user_input: str) -> bool:
        """Handle navigation commands. Returns True if command was handled."""
        cmd = user_input.lower().strip()
        
        # Basic navigation
        if cmd in ['next', 'n', '']:
            if self.current_step < len(self.steps) - 1:
                self.current_step += 1
                self.save_progress()
            return True
            
        elif cmd in ['prev', 'p']:
            if self.current_step > 0:
                self.current_step -= 1
                self.save_progress()
            return True
            
        elif cmd in ['skip', 's']:
            if questionary.confirm("Are you sure you want to skip this step?").ask():
                self.current_step += 1
                self.save_progress()
            return True
            
        elif cmd in ['exit', 'q', 'quit']:
            if questionary.confirm("Are you sure you want to exit the tutorial?").ask():
                return 'exit'
            return True
            
        elif cmd in ['help', 'h']:
            self.show_help()
            input("\nPress Enter to continue...")
            return True
            
        elif cmd == 'hint':
            self.show_hint()
            input("\nPress Enter to continue...")
            return True
            
        # Advanced navigation
        elif cmd.startswith('goto '):
            try:
                step_num = int(cmd.split()[1])
                if self.goto_step(step_num):
                    return True
                else:
                    print(f"{format_text('red')}Invalid step number. Use 'list' to see available steps.{reset_format()}")
            except (ValueError, IndexError):
                print(f"{format_text('red')}Invalid command. Use 'goto <number>'.{reset_format()}")
            return True
            
        elif cmd in ['list', 'ls']:
            self.list_steps()
            input("\nPress Enter to continue...")
            return True
            
        elif cmd == 'reset':
            if questionary.confirm("Are you sure you want to reset the tutorial?").ask():
                self.reset_progress()
            return True
            
        elif cmd == 'save':
            self.save_progress()
            print(f"{format_text('green')}Progress saved!{reset_format()}")
            return True
            
        elif cmd == 'load':
            self.load_progress()
            print(f"{format_text('green')}Progress loaded!{reset_format()}")
            return True
            
        return False

    def run(self):
        try:
            while self.current_step < len(self.steps):
                # Clear screen at the beginning of each step's display cycle
                clear_screen() # Use the helper function
                
                step = self.steps[self.current_step]
                
                # Show progress
                print(f"{format_text('yellow', bold=True)}Step {self.current_step + 1}/{len(self.steps)}: {step.title}{reset_format()}\n")
                
                # Show content
                print(step.content)
                
                # Show exercise if present
                if step.exercise:
                    print(f"\n{format_text('cyan', bold=True)}Exercise:{reset_format()}")
                    print(step.exercise)
                
                # Show navigation options
                print(f"\n{format_text('yellow', bold=True)}Navigation:{reset_format()}")
                print("next/n: Next step    prev/p: Previous step    skip/s: Skip step")
                print("help/h: Show help    hint: Get hint          exit/q: Quit")
                print("goto <n>: Jump to step    list/ls: List steps    reset: Start over")
                
                # Get user input
                user_input = input("\n> ").strip()
                
                # Handle navigation
                result = self.handle_navigation(user_input)
                if result == 'exit':
                    break
                
                # If navigation command was handled, continue to next loop iteration
                if result:
                    continue # The navigation handler already takes care of 'Press Enter to continue...' if needed
                
                # Handle exercise validation (if not a navigation command)
                if step.exercise:
                    display_output = None
                    if step.dynamic_output_generator:
                        generated = step.dynamic_output_generator(user_input)
                        if generated is not None:
                            display_output = generated

                    # Always show simulated output if generated, for exercise steps
                    if display_output:
                        print(f"\n{format_text('yellow', bold=True)}Simulated Output:{reset_format()}")
                        print(display_output)
                        sys.stdout.flush() # Ensure output is immediately visible
                        time.sleep(2.0) # Increased pause to help visibility
                    
                    if step.validation:
                        if step.validation(user_input):
                            print(f"\n{format_text('green')}Correct!{reset_format()}")
                            input("\nPress Enter to continue...") # Acknowledge success
                            self.current_step += 1
                            self.save_progress()
                        else:
                            pass # Do nothing, just let the loop re-display the step
                    else:
                        # If no specific validation, just show output and move to the next step
                        print(f"\n{format_text('yellow')}Input received. Continuing...{reset_format()}")
                        input("\nPress Enter to continue...")
                        self.current_step += 1
                        self.save_progress()
                else:
                    # Input is not a navigation command, and it's not an exercise step.
                    # This is an unrecognized command in a non-exercise context.
                    print(f"\n{format_text('red', bold=True)}Error: Unrecognized command or input.{reset_format()}")
                    print(f"Please use navigation commands (e.g., 'next', 'help') to continue, or press Enter to advance.")
                    input("\nPress Enter to continue...") # Acknowledge error, stay on step until navigation

            # The screen clearing happens at the beginning of the next loop iteration, after user acknowledges current step's output
            if self.current_step >= len(self.steps):
                print(f"\n{format_text('green', bold=True)}Tutorial completed!{reset_format()}")
                if questionary.confirm("Would you like to reset the tutorial progress?").ask():
                    self.reset_progress()
        except KeyboardInterrupt:
            print(f"\n\n{format_text('yellow', bold=True)}Tutorial interrupted. Goodbye!{reset_format()}")
            return

def start_tutorial():
    clear_screen() # Clear screen once at the very beginning of the tutorial
    tutorial = Tutorial()
    tutorial.run()