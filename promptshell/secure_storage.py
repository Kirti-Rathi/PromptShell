import keyring
import os
from .format_utils import format_text, reset_format

SERVICE_NAME = "PromptShell"
SECURE_STORAGE_PLACEHOLDER = "🔒 SECURE_STORAGE"

try:
    from keyrings.alt.file import PlaintextKeyring
    keyring.set_keyring(PlaintextKeyring())
except ImportError:
    pass  # Proceed without keyrings.alt
except Exception as e:
    print(format_text('yellow') + f"⚠️ Keyring setup warning: {str(e)}" + reset_format())

def set_api_key(provider: str, api_key: str):
    """Securely store API key in system keyring"""
    try:
        keyring.set_password(SERVICE_NAME, provider, api_key)
        return True
    except Exception as e:
        print(format_text('red') + f"Secure storage failed: {str(e)}" + reset_format())
        print(format_text('yellow') + "Falling back to config file storage" + reset_format())
        return False

def get_api_key(provider: str) -> str:
    """Retrieve API key from system keyring"""
    try:
        return keyring.get_password(SERVICE_NAME, provider)
    except Exception as e:
        print(format_text('red') + f"Secure retrieval failed: {str(e)}" + reset_format())
        return None

def migrate_config_keys(config: dict):
    """Migrate plaintext keys to secure storage"""
    providers = [
        'GROQ', 'OPENAI', 'GOOGLE', 'ANTHROPIC',
        'FIREWORKS', 'OPENROUTER', 'DEEPSEEK'
    ]
    
    migrated = False
    for provider in providers:
        key = f"{provider}_API_KEY"
        if key not in config or not config[key] or config[key] == SECURE_STORAGE_PLACEHOLDER:
            continue
        if set_api_key(provider, config[key]):
            config[key] = SECURE_STORAGE_PLACEHOLDER
            migrated = True
    
    return migrated