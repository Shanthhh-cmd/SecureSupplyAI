import re
import os
from typing import List, Dict, Any, Tuple

class SuspiciousAnalysisEngine:
    OBFUSCATION_PATTERNS = [
        (r'eval\s*\(\s*base64', "Base64 decode inside eval() execution"),
        (r'exec\s*\(\s*zlib', "Zlib decompression inside exec() execution"),
        (r'__import__\s*\(\s*[\'"]builtins[\'"]\s*\)', "Dynamic builtin module import"),
        (r'\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){10,}', "High concentration of hex-encoded byte strings"),
        (r'String\.fromCharCode\s*\(', "JavaScript String.fromCharCode payload assembly")
    ]

    SHELL_EXEC_PATTERNS = [
        (r'subprocess\.(Popen|run|call|check_output)\s*\(.*shell\s*=\s*True', "Python shell command execution with shell=True"),
        (r'os\.system\s*\(', "Direct os.system command invocation"),
        (r'child_process\.(exec|spawn|execSync)\s*\(', "Node.js child_process command execution"),
        (r'Runtime\.getRuntime\(\)\.exec\s*\(', "Java Runtime.getRuntime().exec shell command execution")
    ]

    NETWORK_INDICATOR_PATTERNS = [
        (r'https?://(?:[0-9]{1,3}\.){3}[0-9]{1,3}', "Hardcoded raw IPv4 address HTTP request target"),
        (r'https?://(?:discord\.com/api/webhooks|pastebin\.com|ngrok\.io|requestbin)', "Known exfiltration domain / webhook endpoint detected"),
        (r'socket\.(socket|connect)\s*\(', "Raw TCP socket connection initialization")
    ]

    INSTALL_SCRIPT_PATTERNS = [
        (r'["\']postinstall["\']\s*:\s*["\'].*sh.*["\']', "NPM postinstall shell script hook"),
        (r'["\']preinstall["\']\s*:\s*["\'].*curl.*["\']', "NPM preinstall curl script downloader hook"),
        (r'cmdclass\s*=\s*\{.*install.*\}', "Custom Python setup.py install command override")
    ]

    @classmethod
    def analyze_code_content(cls, code: str) -> Tuple[float, List[str]]:
        suspicion_score = 0.0
        reasons = []

        # Check Obfuscation
        for pattern, msg in cls.OBFUSCATION_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                suspicion_score += 25.0
                reasons.append(f"OBFUSCATION: {msg}")

        # Check Shell Execution
        for pattern, msg in cls.SHELL_EXEC_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                suspicion_score += 20.0
                reasons.append(f"SHELL_EXEC: {msg}")

        # Check Network Indicators
        for pattern, msg in cls.NETWORK_INDICATOR_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                suspicion_score += 30.0
                reasons.append(f"SUSPICIOUS_NETWORK: {msg}")

        # Check Install Hooks
        for pattern, msg in cls.INSTALL_SCRIPT_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                suspicion_score += 25.0
                reasons.append(f"SUSPICIOUS_INSTALL_HOOK: {msg}")

        suspicion_score = min(suspicion_score, 100.0)
        return suspicion_score, reasons

    @classmethod
    def analyze_package_heuristics(cls, package_name: str, ecosystem: str) -> Tuple[float, List[str]]:
        suspicion_score = 0.0
        reasons = []

        pkg_lower = package_name.lower()

        # Known suspicious test/malicious package names
        SUSPICIOUS_NAMES = ["flatmap-stream", "event-stream-malicious", "reqeusts-stealer", "discord-token-grabber", "node-ipc-malicious"]

        if any(bad in pkg_lower for bad in SUSPICIOUS_NAMES):
            suspicion_score += 85.0
            reasons.append(f"KNOWN_SUSPICIOUS_PACKAGE: Package {package_name} matches known malicious signature database")

        # Package name heuristics: excessively random or numbers appended
        if re.search(r'[a-z]{3,}\d{5,}$', pkg_lower):
            suspicion_score += 30.0
            reasons.append("SUSPICIOUS_NAME: Package name contains highly irregular trailing numeric pattern")

        return suspicion_score, reasons
