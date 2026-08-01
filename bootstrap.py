import sys
import platform
import subprocess
import uuid
import hashlib
import tkinter as tk
from tkinter import messagebox
import urllib.request
import json
import config
from core.chrome_utils import obter_caminho_chrome

# 🔗 Link Raw direto do repositório no GitHub
URL_LICENCAS_GITHUB = "https://raw.githubusercontent.com/josealcimarnunes-stack/licencas-WEBSTRUCT_ANALYZER-/main/licencas.json"


def obter_device_id():
    """Gera um Hash único e persistente baseado no Hardware ID da máquina."""
    try:
        if platform.system() == "Windows":
            cmd = 'powershell "Get-CimInstance -ClassName Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"'
            output = subprocess.check_output(cmd, shell=True).decode().strip()
            if output:
                return output
        elif platform.system() == "Linux":
            with open("/etc/machine-id", "r") as f:
                return f.read().strip()
        elif platform.system() == "Darwin":
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
            return (
                subprocess.check_output(cmd, shell=True).decode().split('"')[3].strip()
            )
    except Exception:
        pass

    raw_id = f"{platform.node()}-{uuid.getnode()}"
    return hashlib.sha256(raw_id.encode()).hexdigest()[:24].upper()


def exibir_popup_licenca(device_id):
    """Exibe pop-up nativo do Windows com o Device ID e instrução de cópia."""
    root = tk.Tk()
    root.withdraw()

    root.clipboard_clear()
    root.clipboard_append(device_id)

    mensagem = (
        "🔒 ATIVAÇÃO DE DISPOSITIVO REQUERIDA\n\n"
        "Este dispositivo não possui uma licença ativa registrada no servidor.\n\n"
        f"Seu Hardware ID:\n{device_id}\n\n"
        "(O código foi copiado automaticamente para sua área de transferência!)\n"
        "Envie este ID para o suporte para liberar o seu acesso."
    )

    messagebox.showwarning("Licença Não Encontrada", mensagem)
    root.destroy()


def checar_licenca_github(device_id):
    """Valida o Device ID contra a lista remota no GitHub."""
    try:
        req = urllib.request.Request(
            URL_LICENCAS_GITHUB, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                licencas_autorizadas = json.loads(response.read().decode())
                return device_id in licencas_autorizadas
    except Exception as e:
        print(f"    ❌ Erro ao consultar servidor de licenças no GitHub: {e}")
        return False

    return False


def validar_ambiente_chrome():
    """Verifica se o Google Chrome nativo está instalado na máquina."""
    print("    🔍 Verificando presença do Google Chrome...")
    caminho_chrome = obter_caminho_chrome()

    if not caminho_chrome:
        print("\n❌ ERRO CRÍTICO: Google Chrome não encontrado!")
        print(
            "👉 Instrução ao Usuário: Por favor, instale o Google Chrome oficial na máquina para poder rodar o bot.\n"
        )

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Google Chrome Não Encontrado",
            "O Google Chrome não foi localizado neste computador.\n\n"
            "Por favor, instale o Google Chrome e rode a aplicação novamente.",
        )
        root.destroy()
        sys.exit(0)

    print(f"    🟢 Chrome localizado em: {caminho_chrome}")
    return True


def preparar_ambiente():
    """Executa todas as travas e validações de infraestrutura antes de abrir o servidor."""
    print("\n[1/3] ⚙️  Iniciando Verificação de Infraestrutura...")

    # 1. Checa Navegador
    validar_ambiente_chrome()

    # 2. Obtém e valida ID da Máquina
    device_id = obter_device_id()
    config.DEVICE_ID = device_id
    print(f"[2/3] 🔑 Validando licença do dispositivo [{device_id}]...")

    # 3. Valida Licença Remota (GitHub)
    licenca_ativa = checar_licenca_github(device_id)

    if not licenca_ativa:
        print("    🔴 Dispositivo NÃO LICENCIADO! Interrompendo boot...")
        exibir_popup_licenca(device_id)
        sys.exit(0)

    print("[3/3] 🟢 Licença e ambiente 100% VALIDADOS!\n")
    return True
