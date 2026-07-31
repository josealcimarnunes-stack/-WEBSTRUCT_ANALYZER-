"""
ESTRATÉGIAS DE MAPEAMENTO PARA SITES COM ANTI-BOT
Vai tentando do mais leve pro mais pesado!
COM SUPORTE A PERFIL DO CHROME REAL!
"""

from playwright.sync_api import sync_playwright
import time
import os
import platform

# ============================================
# ⭐ FUNÇÃO PARA ENCONTRAR O CHROME REAL ⭐
# ============================================


def encontrar_chrome_real():
    """Encontra o caminho do Chrome REAL instalado no sistema"""
    sistema = platform.system()

    if sistema == "Windows":
        caminhos = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            os.path.expanduser("~/AppData/Local/Google/Chrome/Application/chrome.exe"),
        ]
        for caminho in caminhos:
            if os.path.exists(caminho):
                return caminho

    elif sistema == "Darwin":  # macOS
        caminho = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(caminho):
            return caminho

    else:  # Linux
        caminhos = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
        ]
        for caminho in caminhos:
            if os.path.exists(caminho):
                return caminho

    return None


def encontrar_perfil_chrome():
    """Procura a pasta de perfil do Chrome REAL"""
    sistema = platform.system()
    usuario = os.path.expanduser("~")

    if sistema == "Windows":
        caminhos = [
            os.path.join(usuario, "AppData", "Local", "Google", "Chrome", "User Data"),
            os.path.join(usuario, "AppData", "Local", "Chromium", "User Data"),
        ]
    elif sistema == "Darwin":  # macOS
        caminhos = [
            os.path.join(usuario, "Library", "Application Support", "Google", "Chrome"),
            os.path.join(usuario, "Library", "Application Support", "Chromium"),
        ]
    else:  # Linux
        caminhos = [
            os.path.join(usuario, ".config", "google-chrome"),
            os.path.join(usuario, ".config", "chromium"),
        ]

    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho

    return None


# ⭐ GUARDA OS CAMINHOS ⭐
CAMINHO_CHROME_REAL = encontrar_chrome_real()
CAMINHO_PERFIL_CHROME = encontrar_perfil_chrome()


def verificar_modo_anonimo():
    """Verifica se o sistema está em modo anônimo"""
    return CAMINHO_PERFIL_CHROME is None


# ============================================
# ⭐ ARGUMENTOS ANTI-DETECÇÃO ⭐
# ============================================

ARGS_ANTI_DETECCAO = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    "--disable-features=IsolateOrigins,site-per-process",
    "--disable-web-security",
    "--disable-features=BlockInsecurePrivateNetworkRequests",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-background-networking",
    "--disable-client-side-phishing-detection",
    "--disable-component-extensions-with-background-pages",
    "--disable-component-update",
    "--disable-domain-reliability",
    "--disable-logging",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--disable-setuid-sandbox",
    "--disable-wake-on-wifi",
    "--metrics-recording-only",
    "--no-first-run",
    "--no-default-browser-check",
    "--no-pings",
    "--safebrowsing-disable-auto-update",
    "--use-gl=swiftshader",
]


# ============================================
# ⭐ ESTRATÉGIA 1: HEADLESS (MAIS LEVE) ⭐
# ============================================


def estrategia_headless(url, cookies=None):
    print("🔇 [1] Tentando em modo headless (invisível)...")

    with sync_playwright() as p:
        launch_options = {
            "headless": True,
            "args": ARGS_ANTI_DETECCAO,
        }

        if CAMINHO_CHROME_REAL:
            launch_options["executable_path"] = CAMINHO_CHROME_REAL
            print(f"   ✅ Usando Chrome REAL")

        if CAMINHO_PERFIL_CHROME:
            launch_options["user_data_dir"] = CAMINHO_PERFIL_CHROME
            print(f"   ✅ Usando perfil do Chrome")

        browser = p.chromium.launch(**launch_options)
        context = browser.new_context()

        if cookies:
            context.add_cookies(cookies)
            print(f"   🍪 Adicionados {len(cookies)} cookies")

        page = context.new_page()
        page.goto(url, timeout=30000)
        page.wait_for_timeout(2000)

        elementos = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('*')).map(el => ({
                tag: el.tagName.toLowerCase(),
                classe: el.className || '',
                id: el.id || '',
                texto: (el.innerText || '').trim().slice(0, 100)
            }));
        }""")

        browser.close()
        print(f"   ✅ Encontrou {len(elementos)} elementos")
        return elementos


# ============================================
# ⭐ ESTRATÉGIA 2: NORMAL (JANELA VISÍVEL) ⭐
# ============================================


def estrategia_normal(url, cookies=None):
    print("🪟 [2] Abrindo navegador visível...")

    with sync_playwright() as p:
        launch_options = {
            "headless": False,
            "args": ARGS_ANTI_DETECCAO,
        }

        if CAMINHO_CHROME_REAL:
            launch_options["executable_path"] = CAMINHO_CHROME_REAL
            print(f"   ✅ Usando Chrome REAL")

        if CAMINHO_PERFIL_CHROME:
            launch_options["user_data_dir"] = CAMINHO_PERFIL_CHROME
            print(f"   ✅ Usando perfil do Chrome com cookies")

        browser = p.chromium.launch(**launch_options)
        context = browser.new_context()

        if cookies:
            context.add_cookies(cookies)
            print(f"   🍪 Adicionados {len(cookies)} cookies")

        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        elementos = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('*')).map(el => ({
                tag: el.tagName.toLowerCase(),
                classe: el.className || '',
                id: el.id || '',
                texto: (el.innerText || '').trim().slice(0, 100)
            }));
        }""")

        browser.close()
        print(f"   ✅ Encontrou {len(elementos)} elementos")
        return elementos


# ============================================
# ⭐ ESTRATÉGIA 3: STEALTH (ESCONDE QUE É BOT) ⭐
# ============================================


def estrategia_stealth(url, cookies=None):
    print("🕵️ [3] Tentando esconder que é bot...")

    with sync_playwright() as p:
        launch_options = {
            "headless": False,
            "args": ARGS_ANTI_DETECCAO,
        }

        if CAMINHO_CHROME_REAL:
            launch_options["executable_path"] = CAMINHO_CHROME_REAL
            print(f"   ✅ Usando Chrome REAL")

        if CAMINHO_PERFIL_CHROME:
            launch_options["user_data_dir"] = CAMINHO_PERFIL_CHROME
            print(f"   ✅ Usando perfil do Chrome com cookies")

        browser = p.chromium.launch(**launch_options)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        if cookies:
            context.add_cookies(cookies)
            print(f"   🍪 Adicionados {len(cookies)} cookies")

        page = context.new_page()

        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000)

        page.mouse.move(100, 100)
        page.wait_for_timeout(500)
        page.mouse.move(200, 200)

        elementos = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('*')).map(el => ({
                tag: el.tagName.toLowerCase(),
                classe: el.className || '',
                id: el.id || '',
                texto: (el.innerText || '').trim().slice(0, 100)
            }));
        }""")

        browser.close()
        print(f"   ✅ Encontrou {len(elementos)} elementos")
        return elementos


# ============================================
# ⭐ ESTRATÉGIA 4: FINGERPRINT REAL ⭐
# ============================================


def estrategia_fingerprint(url, cookies=None):
    print("🎭 [4] Simulando usuário real completo...")

    with sync_playwright() as p:
        launch_options = {
            "headless": False,
            "args": ARGS_ANTI_DETECCAO,
        }

        if CAMINHO_CHROME_REAL:
            launch_options["executable_path"] = CAMINHO_CHROME_REAL
            print(f"   ✅ Usando Chrome REAL")

        if CAMINHO_PERFIL_CHROME:
            launch_options["user_data_dir"] = CAMINHO_PERFIL_CHROME
            print(f"   ✅ Usando perfil do Chrome com cookies")

        browser = p.chromium.launch(**launch_options)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )

        if cookies:
            context.add_cookies(cookies)
            print(f"   🍪 Adicionados {len(cookies)} cookies")

        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)

        for i in range(3):
            page.mouse.move(100 + (i * 150), 200 + (i * 50))
            page.wait_for_timeout(500)

        elementos = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('*')).map(el => ({
                tag: el.tagName.toLowerCase(),
                classe: el.className || '',
                id: el.id || '',
                texto: (el.innerText || '').trim().slice(0, 100)
            }));
        }""")

        browser.close()
        print(f"   ✅ Encontrou {len(elementos)} elementos")
        return elementos


# ============================================
# ⭐ FUNÇÃO PRINCIPAL ⭐
# ============================================


def analisar_com_todas_estrategias(url, cookies=None):
    print("\n" + "=" * 60)
    print(f"🎯 MAPEANDO: {url}")
    if CAMINHO_PERFIL_CHROME:
        print(f"✅ USANDO PERFIL DO CHROME: {CAMINHO_PERFIL_CHROME}")
    else:
        print("⚠️ MODO ANÔNIMO (sem perfil)")
    print("=" * 60 + "\n")

    estrategias = [
        estrategia_headless,
        estrategia_normal,
        estrategia_stealth,
        estrategia_fingerprint,
    ]

    for func in estrategias:
        try:
            elementos = func(url, cookies)
            if len(elementos) > 50:
                print(f"\n✅ SUCESSO! {len(elementos)} elementos mapeados!")
                return elementos
            else:
                print(f"   ⚠️ Poucos elementos ({len(elementos)}), tentando próximo...")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            continue

    print("\n❌ Todas as estratégias falharam!")
    return []
