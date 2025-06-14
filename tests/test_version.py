import subprocess
import sys
import os
import shutil

def test_version_flag():
    # Try to find promptshell in PATH
    promptshell_cmd = shutil.which("promptshell")
    
    if not promptshell_cmd:
        # If not in PATH, try to find it in the Python scripts directory
        python_scripts = os.path.join(sys.prefix, "Scripts" if sys.platform == "win32" else "bin")
        promptshell_cmd = os.path.join(python_scripts, "promptshell")
        
        if not os.path.exists(promptshell_cmd):
            raise FileNotFoundError(
                "Could not find promptshell command. Make sure you have installed the package "
                "using 'pip install -e .' in the project root directory."
            )

    print(f"Testing with promptshell at: {promptshell_cmd}")

    # Run the command with --version flag
    try:
        result = subprocess.run(
            [promptshell_cmd, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise AssertionError(f"Command failed with error: {e.stderr}")

    # Check if output matches expected format
    output = result.stdout.strip()
    if not output.startswith("PromptShell v"):
        raise AssertionError(f"Unexpected output format: {output}")
    
    # Verify version number format (x.y.z)
    version = output.split("v")[1]
    version_parts = version.split(".")
    if len(version_parts) != 3:
        raise AssertionError(f"Invalid version format: {version}")
    if not all(part.isdigit() for part in version_parts):
        raise AssertionError(f"Version parts should be numbers: {version}")

    print(f"Successfully verified version: {output}")

if __name__ == "__main__":
    test_version_flag()
    print("Version flag test passed successfully!") 