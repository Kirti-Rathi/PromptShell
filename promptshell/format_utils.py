import os
import platform

def format_text(fg, bg=None, inverted=False, bold=False):
    reset = "\033[0m"
    result = reset
    if bold:
        result += "\033[1m"
    if inverted:
        result += "\033[7m"
    fg_codes = {'black': '30', 'red': '31', 'green': '32', 'yellow': '33', 
                'blue': '34', 'magenta': '35', 'cyan': '36', 'white': '37'}
    bg_codes = {'black': '40', 'red': '41', 'green': '42', 'yellow': '43', 
                'blue': '44', 'magenta': '45', 'cyan': '46', 'white': '47'}
    result += f'\033[{fg_codes.get(fg, "37")}m'
    if bg:
        result += f'\033[{bg_codes.get(bg, "40")}m'
    return result

def reset_format():
    return "\033[0m"

def get_terminal_size():
    try:
        columns, rows = os.get_terminal_size(0)
    except OSError:
        columns, rows = os.get_terminal_size(1)
    return columns, rows

def get_current_os():
    """Detect and normalize current operating system"""
    system = platform.system().lower()
    return 'windows' if system == 'windows' else 'macos' if system == 'darwin' else 'linux'

def get_os_specific_examples():
    """Return OS-appropriate command examples"""
    current_os = get_current_os()
    examples = {
        'windows': [
            '"List files" -> dir',
            '"Create directory" -> mkdir projects',
            '"Delete file" -> del example.txt',
            '"Copy file" -> copy source.txt destination.txt',
            '"Search text" -> findstr "pattern" file.txt'
        ],
        'linux': [
            '"List files" -> ls -l',
            '"Create directory" -> mkdir projects',
            '"Delete file" -> rm example.txt',
            '"Copy file" -> cp source.txt destination.txt',
            '"Search text" -> grep "pattern" file.txt'
        ],
        'macos': [
            '"List files" -> ls -lG',
            '"Create directory" -> mkdir projects',
            '"Delete file" -> rm example.txt',
            '"Copy file" -> cp source.txt destination.txt',
            '"Search text" -> grep "pattern" file.txt'
        ]
    }
    return examples[current_os]