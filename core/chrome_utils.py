import os
import sys
import platform
from pathlib import Path
import config

ARGS_ANTI_DETECCAO = [
    "--disable-blink-features=AutomationControlled",
    "--disable-infobars",
    "--no-first-run",
    "--no-service-autorun",
    "--password-store=basic",
    "--use-mock-keychain",
    "--ignore-certificate-errors",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--disable-component-extensions-with-background-pages",
    "--disable-default-apps",
    "--disable-extensions",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-sync",
    "--enable-automation",
]


def obter_caminho_chrome():
    """Detecta instalações do Google Chrome nativo no sistema operacional."""
    sistema = platform.system()
    candidatos = []

    if sistema == "Windows":
        candidatos = [
            Path(os.environ.get("PROGRAMFILES", "C:\\Program Files"))
            / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"))
            / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("LOCALAPPDATA", ""))
            / "Google\\Chrome\\Application\\chrome.exe",
        ]
    elif sistema == "Linux":
        candidatos = [
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/chrome"),
            Path("/usr/bin/chromium-browser"),
            Path("/usr/bin/chromium"),
        ]
    elif sistema == "Darwin":
        candidatos = [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]

    for caminho in candidatos:
        if caminho.exists():
            return str(caminho)

    return None


def obter_perfil_chrome_dir():
    """Retorna o caminho do diretório isolado do perfil de usuário."""
    return str(config.CHROME_PROFILE_DIR)
