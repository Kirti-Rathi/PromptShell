import questionary
import requests
import os
from .format_utils import format_text, reset_format
from .secure_storage import set_api_key, migrate_config_keys, get_api_key

# Determine the configuration directory based on the operating system
if os.name == 'nt':  # Windows
    CONFIG_DIR = os.path.join(os.getenv('APPDATA'), 'PromptShell')
else:  # Linux/macOS
    CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'PromptShell')

# Ensure the configuration directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(CONFIG_DIR, "promptshell_config.conf")
warning_printed = False  # Global variable to track if the warning has been printed

def setup_wizard():
    """Interactive configuration setup wizard."""

    # Load existing configuration
    config = load_config()

    # Select Operation Mode
    operation_mode = questionary.select(
        "Select operation mode:",
        choices=[
            "local (Privacy-first, needs 4GB+ RAM)",
            "api (Faster but requires internet)"
        ]
    ).ask()
    if not operation_mode:
        print(format_text("yellow") + "⚠️ Operation mode selection cancelled. Exiting setup." + reset_format())
        return
    operation_mode = operation_mode.split()[0]  # Extract "local" or "api"

    # Default values
    ollama_host = "http://localhost:11434"
    local_model = "llama3:8b-instruct-q4_1"
    api_provider = None
    api_model = None

    API_PROVIDER_MODELS = {
        "Groq": ['llama-3.1-8b-instant', 'deepseek-r1-distill-llama-70b', 'gemma2-9b-it', 'llama-3.3-70b-versatile', 'llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768'],
        "OpenAI": ['gpt-4o', 'chatgpt-4o-latest', 'o1', 'o1-mini', 'o1-preview', 'gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        "Google": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro"],
        "Anthropic": ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
        "Fireworks": ["mixtral-8x7b-instruct", "llama-v3p3-70b-instruct", "llama-v3p1-8b-instruct", "llama-v3p1-405b-instruct", "deepseek-v3"],
        "OpenRouter": ["google/gemini-2.0-flash-thinking-exp:free"],
        "Deepseek": ["deepseek-chat"]
    }

    def get_installed_models():
        """Fetch installed models from local Ollama server"""
        try:
            response = requests.get(f"{ollama_host}/api/tags")
            response.raise_for_status()
            models = [model["name"] for model in response.json().get("models", [])]
            
            return [
                model for model in models
            ]
        except requests.exceptions.RequestException as e:
            print(format_text("yellow") + f"⚠️ Could not connect to Ollama: {e}" + reset_format())
        return []
    
    installed_models = get_installed_models()

    # If Local mode is selected, choose a model
    if operation_mode == "local":
        if not installed_models:
            print(format_text("yellow", bold=True) + "⚠️ No models found on the local Ollama server. Please install models and try again." + reset_format())
            return
        local_model = questionary.select(
            "Choose local model:",
            choices=[
                *installed_models,
            ]
        ).ask()
        if not local_model:
            print(format_text("yellow") + "⚠️ Local model selection cancelled. Exiting setup." + reset_format())
            return
        local_model = local_model.split()[0]  # Extract model name

    # If API mode is selected, choose provider, then model, then API key
    api_key_dict = {
        "Groq": "",
        "OpenAI": "",
        "Google": "",
        "Anthropic": "",
        "Fireworks": "",
        "OpenRouter": "",
        "Deepseek": ""
    }

    if operation_mode == "api":
        api_provider = questionary.select(
            "API provider selection:",
            choices=list(api_key_dict.keys())
        ).ask()
        if not api_provider:
            print(format_text("yellow") + "⚠️ API provider selection cancelled. Exiting setup." + reset_format())
            return

        # Get available models for the selected provider
        provider_models = API_PROVIDER_MODELS.get(api_provider, [])
        
        # Add custom option and set default
        model_choices = provider_models + ["Custom model..."]
        default_model = provider_models[0] if provider_models else ""
        
        api_model = questionary.select(
            f"Select model for {api_provider}:",
            choices=model_choices,
            default=default_model
        ).ask()
        if not api_model:
            print(format_text("yellow") + "⚠️ API model selection cancelled. Exiting setup." + reset_format())
            return
        
        # Handle custom model input
        if api_model == "Custom model...":
            api_model = questionary.text(
                f"Enter custom model name for {api_provider}:",
                default=default_model
            ).ask()
            if not api_model:
                print(format_text("yellow") + "⚠️ Custom model input cancelled. Exiting setup." + reset_format())
                return

        provider_key_name = f"{api_provider.upper()}_API_KEY"
        if provider_key_name in config and config[provider_key_name]:
            existing_api = questionary.confirm(
                f"API key for {api_provider} already exists. Do you want to use it?"
            ).ask()
            if existing_api is None:
                print(format_text("yellow") + "⚠️ API key confirmation cancelled. Exiting setup." + reset_format())
                return
            if existing_api:
                # Retrieve key from secure storage
                secure_key = get_api_key(api_provider)
                if secure_key:
                    api_key_dict[api_provider] = secure_key
                else:
                    print(format_text("yellow") + "⚠️ Failed to retrieve secure key. Please enter it again." + reset_format())
                    api_key_dict[api_provider] = questionary.password(
                        f"Enter API key for {api_provider}:"
                    ).ask()
            else:
                # Ask for new key if not reusing
                api_key_dict[api_provider] = questionary.password(
                    f"Enter API key for {api_provider}:"
                ).ask()
        else:
            # Ask for API key securely if not already saved
            api_key_dict[api_provider] = questionary.password(
                f"Enter API key for {api_provider}:"
            ).ask()
        if not api_key_dict[api_provider]:
            print(format_text("yellow") + "⚠️ API key input cancelled. Exiting setup." + reset_format())
            return

    # Merge new configuration with existing configuration
    config["MODE"] = operation_mode
    config["OLLAMA_HOST"] = ollama_host
    config["LOCAL_MODEL"] = local_model
    config["ACTIVE_API_PROVIDER"] = api_provider.lower() if api_provider else "None"
    config["API_MODEL"] = api_model if api_model else " "

    # Update only the selected provider's API key
    if api_provider:
        # Store key securely
        if api_key_dict[api_provider]:
            if set_api_key(api_provider, api_key_dict[api_provider]):
                config[f"{api_provider.upper()}_API_KEY"] = "🔒 SECURE_STORAGE"
            else:
                # Fallback to config if secure storage fails
                config[f"{api_provider.upper()}_API_KEY"] = api_key_dict[api_provider]
                print(format_text("yellow") + "Warning: API key stored in config file instead of secure storage." + reset_format())

    # Generate Configuration File
    config_content = generate_config_content(config)

    with open(CONFIG_FILE, "w", encoding='utf-8') as file:
        file.write(config_content)

    print(format_text("green", bg="black") + f"\n✅ Configuration updated!" + reset_format())
    print(format_text("blue") + f"Active model: {get_active_model()}" + reset_format())

def load_config():
    """
    Loads the configuration file into a dictionary.
    Returns default values if the file is missing or incomplete.
    """
    global warning_printed  

    config = {
        "MODE": "local",
        "OLLAMA_HOST": "http://localhost:11434",
        "LOCAL_MODEL": "llama3:8b-instruct-q4_1",
        "ACTIVE_API_PROVIDER": "groq",
        "API_MODEL": "mixtral-8x7b-32768",
        "GROQ_API_KEY": "",
        "OPENAI_API_KEY": "",
        "GOOGLE_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "FIREWORKS_API_KEY": "",
        "OPENROUTER_API_KEY": "",
        "DEEPSEEK_API_KEY": "",
    }

    if not os.path.exists(CONFIG_FILE):
        if not warning_printed:
            print(format_text("yellow") + f"⚠️ Config file '{CONFIG_FILE}' not found. Using default settings." + reset_format())
            warning_printed = True  
        return config

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  

                key_value = line.split("=", 1)
                if len(key_value) == 2:
                    key, value = key_value
                    config[key.strip()] = value.strip()

    config["MODE"] = config["MODE"].strip().lower()

    # Migrate keys to secure storage
    migrate_config_keys(config)
    
    return config

def get_active_model():
    """
    Gets active AI model name based on the operation mode.

    Returns the model name.
    Uses 'LOCAL_MODEL' if in local mode, otherwise 'API_MODEL'.
    """
    
    config = load_config()

    if config["MODE"] == "local":
        return config["LOCAL_MODEL"]
    else:
        return config["API_MODEL"]

def get_provider():
    """Gets current AI provider.
    
    Returns:
        Provider name string
    """

    config = load_config()
    if config["MODE"] == "api":
        return config["ACTIVE_API_PROVIDER"]
    else:
        return "ollama"

def generate_config_content(config: dict) -> str:
    """Generate config file content with secure storage indicators"""
    return f"""# PromptShell Configuration
# ------------------------
# Operation Mode (local/api)
MODE={config.get("MODE", "local")}
OLLAMA_HOST={config.get("OLLAMA_HOST", "http://localhost:11434")}
# Local Configuration
LOCAL_MODEL={config.get("LOCAL_MODEL", "llama3:8b-instruct-q4_1")}
# API Configuration
ACTIVE_API_PROVIDER={config.get("ACTIVE_API_PROVIDER", "None")}
API_MODEL={config.get("API_MODEL", " ")}
# Provider API Keys (🔒 indicates secure storage)
GROQ_API_KEY={config.get("GROQ_API_KEY", "")}
OPENAI_API_KEY={config.get("OPENAI_API_KEY", "")}
GOOGLE_API_KEY={config.get("GOOGLE_API_KEY", "")}
ANTHROPIC_API_KEY={config.get("ANTHROPIC_API_KEY", "")}
FIREWORKS_API_KEY={config.get("FIREWORKS_API_KEY", "")}
OPENROUTER_API_KEY={config.get("OPENROUTER_API_KEY", "")}
DEEPSEEK_API_KEY={config.get("DEEPSEEK_API_KEY", "")}
"""