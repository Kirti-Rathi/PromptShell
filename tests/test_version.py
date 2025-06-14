import subprocess
import sys

def test_version_flag():
    print("Running the command to check the version...")

    result = subprocess.run(
        [sys.executable, "-m", "promptshell.main", "--version"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        version_output = result.stdout.strip()
        if version_output.startswith("PromptShell v"):
            print(f"Version output is as expected: {version_output}")
        else:
            print("Unexpected output:")
            print(version_output)
    else:
        print(f"Command failed with return code: {result.returncode}")
        if result.stderr:
            print("Error:", result.stderr)

if __name__ == "__main__":
    test_version_flag()
