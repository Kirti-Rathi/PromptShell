import platform

def get_system_info() -> dict:
    """Retrieve system information as a dictionary with structured data.
    
    Returns:
        Dictionary of system properties
    """
    
    try:
        return {
            'os': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'cpu': platform.processor(),
            'platform': platform.platform(),
        }
    except Exception as e:
        return {
            'error': str(e),
            'os': 'Unknown',
            'release': 'Unknown',
            'version': 'Unknown',
            'machine': 'Unknown',
            'cpu': 'Unknown',
            'platform': 'Unknown'
        }
