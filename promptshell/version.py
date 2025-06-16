import importlib.metadata

def get_version():
    """Get the current version of PromptShell from package metadata."""
    try:
        return importlib.metadata.version("promptshell")
    except importlib.metadata.PackageNotFoundError:
        return "unknown" 