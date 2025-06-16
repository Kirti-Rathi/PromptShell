import platform

if platform.system().lower() == "windows":
    from ctypes import windll, byref
    from ctypes.wintypes import DWORD, HANDLE

    def enable_ansi_support():
        """Enable ANSI escape sequences on Windows"""
        STD_OUTPUT_HANDLE = -11
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        
        hOut = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        dwMode = DWORD()
        windll.kernel32.GetConsoleMode(hOut, byref(dwMode))
        if not dwMode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING:
            dwMode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
            windll.kernel32.SetConsoleMode(hOut, dwMode)
else:
    def enable_ansi_support():
        """No-op function for non-Windows systems"""
        pass
