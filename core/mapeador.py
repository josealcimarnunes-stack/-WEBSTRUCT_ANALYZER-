from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time
import base64
import json
import platform
import sys  # ⭐ ESSENCIAL PARA O getattr(sys, "frozen", False)


def configurar_playwright():
    if os.environ.get("RENDER"):
        # Modo Render
        browsers_path = os.path.join(os.getcwd(), ".cache", "ms-playwright")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
        print(f"✅ Render mode: {browsers_path}")
    elif getattr(sys, "frozen", False):
        # Modo .exe
        browsers_path = os.path.join(sys._MEIPASS, "playwright_browsers")
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
    else:
        # Modo desenvolvimento
        browsers_path = os.path.join(os.getcwd(), "playwright_browsers")
        if os.path.exists(browsers_path):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path


# ⭐ CONFIGURAÇÕES DE TIMEOUT GLOBAIS ⭐
os.environ["PLAYWRIGHT_TIMEOUT"] = "300000"
os.environ["PLAYWRIGHT_WS_TIMEOUT"] = "300000"

TIMEOUT_PAGINA = 120000
TIMEOUT_NAVEGADOR = 60000


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
                print(f"✅ Chrome REAL encontrado em: {caminho}")
                return caminho

    elif sistema == "Darwin":  # macOS
        caminho = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(caminho):
            print(f"✅ Chrome REAL encontrado em: {caminho}")
            return caminho

    else:  # Linux
        caminhos = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
        for caminho in caminhos:
            if os.path.exists(caminho):
                print(f"✅ Chrome REAL encontrado em: {caminho}")
                return caminho

    print("⚠️ Chrome REAL NÃO encontrado! Usando Chromium do Playwright.")
    return None


# ============================================
# ⭐ FUNÇÃO PARA ENCONTRAR PERFIL DO CHROME ⭐
# ============================================


def encontrar_perfil_chrome():
    """
    Cria/retorna um diretório de perfil ISOLADO e exclusivo para o Bot.
    Isso evita conflitos com o Chrome pessoal do usuário que já está em uso
    (reuniões, YouTube, abas abertas) e previne travamentos por arquivo bloqueado.
    """
    # Define a pasta isolada dentro da raiz do projeto
    pasta_perfil_bot = os.path.join(os.getcwd(), "bot_chrome_profile")

    # Cria a pasta caso ela ainda não exista
    if not os.path.exists(pasta_perfil_bot):
        try:
            os.makedirs(pasta_perfil_bot, exist_ok=True)
            print(f"✅ Criado novo perfil isolado para o bot em: {pasta_perfil_bot}")
        except Exception as e:
            print(f"⚠️ Erro ao criar pasta do perfil do bot: {e}")
            return None

    print(f"✅ Usando perfil isolado do Bot: {pasta_perfil_bot}")
    return pasta_perfil_bot


def verificar_modo_anonimo():
    """Verifica se o sistema está em modo anônimo"""
    return encontrar_perfil_chrome() is None


# ⭐ GUARDA O CAMINHO DO CHROME REAL ⭐
CAMINHO_CHROME_REAL = encontrar_chrome_real()
CAMINHO_PERFIL_CHROME = encontrar_perfil_chrome()


# ⭐ FUNÇÕES AUXILIARES ⭐
def gerar_seletor_css(tag, classe, id_elem):
    if id_elem:
        return f"#{id_elem}"
    if classe:
        classes = classe.strip().split()
        if len(classes) == 1:
            return f".{classes[0]}"
        else:
            return f".{'.'.join(classes)}"
    return tag


def gerar_xpath(tag, classe, id_elem, posicao):
    if id_elem:
        return f'//{tag}[@id="{id_elem}"]'
    if classe:
        classes = classe.strip().split()
        return f'//{tag}[contains(@class, "{classes[0]}")]'
    return f"//{tag}[{posicao}]"


# ============================================
# ⭐ FUNÇÃO PARA TIRAR FOTO RÁPIDA ⭐
# ============================================
# ... resto do código continua igual ...

# ============================================
# ⭐ FUNÇÃO PARA TIRAR FOTO RÁPIDA ⭐
# ============================================


def tirar_foto_rapida(url):
    print(f"📸 Tirando foto rápida de: {url}")

    # ⭐ TENTATIVA 1: Chrome REAL com perfil ⭐
    try:
        with sync_playwright() as p:
            if CAMINHO_PERFIL_CHROME and CAMINHO_CHROME_REAL:
                print(f"✅ Tentando Chrome REAL com perfil...")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=CAMINHO_PERFIL_CHROME,
                    headless=False,
                    executable_path=CAMINHO_CHROME_REAL,
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
                )
                page = context.new_page()
                page.goto(url, timeout=60000, wait_until="networkidle")
                page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
                page.wait_for_timeout(1000)
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(1000)
                screenshot = page.screenshot(full_page=False)
                screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
                context.close()
                print("📸 Foto rápida capturada com Chrome REAL!")
                return screenshot_base64
    except Exception as e:
        print(f"⚠️ Chrome REAL falhou: {e}")
        print("🔄 Fallback: usando Chromium do Playwright...")

    # ⭐ FALLBACK: Chromium do Playwright ⭐
    try:
        with sync_playwright() as p:
            print(f"🔄 Usando Chromium do Playwright (fallback)")
            context = p.chromium.launch_persistent_context(
                user_data_dir="/tmp/playwright_temp",
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
            )
            page = context.new_page()
            page.goto(url, timeout=60000, wait_until="networkidle")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
            page.wait_for_timeout(1000)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
            screenshot = page.screenshot(full_page=False)
            screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
            context.close()
            print("📸 Foto rápida capturada com Chromium (fallback)!")
            return screenshot_base64
    except Exception as e:
        print(f"❌ Fallback também falhou: {e}")
        return None


# ============================================
# ⭐ FUNÇÃO DE MAPEAMENTO COM PROGRESSO ⭐
# ============================================


def analisar_estrutura_com_progresso(url):
    print(f"🔍 Analisando: {url}")
    try:
        with sync_playwright() as p:
            # ⭐ TENTA CHROME REAL COM PERFIL ⭐
            try:
                if CAMINHO_PERFIL_CHROME and CAMINHO_CHROME_REAL:
                    print(f"✅ Tentando Chrome REAL com perfil...")
                    context = p.chromium.launch_persistent_context(
                        user_data_dir=CAMINHO_PERFIL_CHROME,
                        headless=True,
                        executable_path=CAMINHO_CHROME_REAL,
                        args=[
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-gpu",
                            "--disable-blink-features=AutomationControlled",
                        ],
                    )
                else:
                    raise Exception("Sem Chrome REAL ou perfil")
            except Exception as e:
                print(f"⚠️ Chrome REAL falhou: {e}")
                print(f"🔄 Fallback: Chromium do Playwright")
                context = p.chromium.launch_persistent_context(
                    user_data_dir="/tmp/playwright_temp",
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-blink-features=AutomationControlled",
                    ],
                )

            page = context.new_page()

            # ⭐ TIMEOUT AUMENTADO ⭐
            page.goto(url, timeout=180000, wait_until="networkidle")
            page.wait_for_selector("body", timeout=30000)

            yield json.dumps({"status": "carregando", "mensagem": "Página carregada!"})

            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.5)")
            page.wait_for_timeout(1500)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
            yield json.dumps({"status": "scroll", "mensagem": "Scroll concluído!"})

            print("⏳ Coletando todos os elementos via evaluate...")
            elementos = page.evaluate("""() => {
                const allElements = document.querySelectorAll('*');
                return Array.from(allElements).map(el => ({
                    tag: el.tagName.toLowerCase(),
                    classe: el.className || '',
                    id: el.id || '',
                    link: el.getAttribute('href') || '',
                    texto: (el.innerText || '').trim().slice(0, 300),
                    profundidade: (() => {
                        let depth = 0;
                        let parent = el.parentElement;
                        while (parent) {
                            depth++;
                            parent = parent.parentElement;
                        }
                        return depth;
                    })(),
                    pai: el.parentElement ? el.parentElement.tagName.toLowerCase() : ''
                }));
            }""")
            print(f"🔍 Total de elementos encontrados: {len(elementos)}")

            dados = []
            for posicao, elem in enumerate(elementos, 1):
                dados.append(
                    {
                        "posicao": posicao,
                        "profundidade": elem.get("profundidade", 0),
                        "tag": elem.get("tag", ""),
                        "classe": elem.get("classe", ""),
                        "id": elem.get("id", ""),
                        "link": elem.get("link", ""),
                        "texto": elem.get("texto", ""),
                        "pai": elem.get("pai", ""),
                        "seletor_css": gerar_seletor_css(
                            elem.get("tag", ""),
                            elem.get("classe", ""),
                            elem.get("id", ""),
                        ),
                        "xpath": gerar_xpath(
                            elem.get("tag", ""),
                            elem.get("classe", ""),
                            elem.get("id", ""),
                            posicao,
                        ),
                    }
                )
                if posicao % 10 == 0 or posicao == len(elementos):
                    pct = int((posicao / len(elementos)) * 100)
                    yield json.dumps(
                        {
                            "status": "progresso",
                            "atual": posicao,
                            "total": len(elementos),
                            "percentual": pct,
                            "mensagem": f"Coletando elementos... {posicao} / {len(elementos)}",
                        }
                    )

            context.close()
            yield json.dumps(
                {
                    "status": "concluido",
                    "total": len(dados),
                    "dados": dados,
                    "mensagem": f"✅ {len(dados)} elementos mapeados!",
                }
            )
    except Exception as e:
        yield json.dumps({"status": "erro", "mensagem": str(e)})


# ============================================
# ⭐ FUNÇÃO DE MAPEAMENTO COMPLETO ⭐
# ============================================


def analisar_estrutura(url, pegar_screenshot=False, headless=True):
    print(f"🔍 Analisando: {url}")
    print(f"🪟 Modo headless: {headless}")
    dados = []
    screenshot_base64 = None

    try:
        with sync_playwright() as p:
            # ⭐ ARGUMENTOS ANTI-DETECÇÃO ⭐
            args = [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-web-security",
                "--disable-features=BlockInsecurePrivateNetworkRequests",
            ]

            launch_options = {
                "headless": headless,
                "timeout": TIMEOUT_NAVEGADOR,
                "args": args,
            }

            # ⭐ USA O CHROME REAL SEMPRE ⭐
            if CAMINHO_CHROME_REAL:
                launch_options["executable_path"] = CAMINHO_CHROME_REAL
                print(f"✅ Usando Chrome REAL em: {CAMINHO_CHROME_REAL}")
            else:
                print("🪟 Usando Chromium do Playwright (modo alternativo)")

            # ⭐ USA O PERFIL SE POSSÍVEL ⭐
            if CAMINHO_PERFIL_CHROME and not headless:
                launch_options["user_data_dir"] = CAMINHO_PERFIL_CHROME
                print(
                    f"✅ Usando perfil do Chrome com cookies: {CAMINHO_PERFIL_CHROME}"
                )

            print(f"🚀 Abrindo navegador... headless={launch_options.get('headless')}")

            browser = p.chromium.launch(**launch_options)

            page = browser.new_page(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )

            timeout = 30000 if headless else 90000
            print(f"⏳ Carregando página... timeout={timeout}ms")

            try:
                page.goto(url, timeout=timeout, wait_until="networkidle")
                print("✅ Página carregada!")
            except Exception as e:
                print(f"⚠️ Erro ao carregar: {e}")
                print("Tentando com wait_until='domcontentloaded'...")
                page.goto(url, timeout=timeout, wait_until="domcontentloaded")

            try:
                page.wait_for_selector("body", timeout=15000)
                print("✅ Body carregado!")
            except:
                print("⚠️ Body não encontrado, continuando...")

            print("⏳ Rolando a página para carregar tudo...")
            for i in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                print(f"  Scroll {i+1}/5")

            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)

            if pegar_screenshot:
                print("📸 Tirando screenshot...")
                page.wait_for_timeout(2000)
                screenshot = page.screenshot(full_page=True)
                screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
                print("📸 Screenshot capturado!")

            print("⏳ Coletando elementos da página...")
            elementos = page.evaluate("""() => {
                const allElements = document.querySelectorAll('*');
                const result = [];
                for (const el of allElements) {
                    const tag = el.tagName.toLowerCase();
                    if (tag === 'html' || tag === 'head' || tag === 'meta' || tag === 'link' || tag === 'script' || tag === 'style') {
                        continue;
                    }
                    result.push({
                        tag: tag,
                        classe: el.className || '',
                        id: el.id || '',
                        link: el.getAttribute('href') || '',
                        texto: (el.innerText || '').trim().slice(0, 300),
                        profundidade: (() => {
                            let depth = 0;
                            let parent = el.parentElement;
                            while (parent) {
                                depth++;
                                parent = parent.parentElement;
                            }
                            return depth;
                        })(),
                        pai: el.parentElement ? el.parentElement.tagName.toLowerCase() : ''
                    });
                }
                return result;
            }""")

            print(f"🔍 Encontrados: {len(elementos)} elementos")

            for posicao, elem in enumerate(elementos, 1):
                dados.append(
                    {
                        "posicao": posicao,
                        "profundidade": elem.get("profundidade", 0),
                        "tag": elem.get("tag", ""),
                        "classe": elem.get("classe", ""),
                        "id": elem.get("id", ""),
                        "link": elem.get("link", ""),
                        "texto": elem.get("texto", ""),
                        "pai": elem.get("pai", ""),
                        "seletor_css": gerar_seletor_css(
                            elem.get("tag", ""),
                            elem.get("classe", ""),
                            elem.get("id", ""),
                        ),
                        "xpath": gerar_xpath(
                            elem.get("tag", ""),
                            elem.get("classe", ""),
                            elem.get("id", ""),
                            posicao,
                        ),
                    }
                )

            browser.close()
            print(f"✅ {len(dados)} elementos mapeados!")

            if pegar_screenshot:
                return dados, screenshot_base64
            else:
                return dados

    except Exception as e:
        print(f"❌ Erro no mapeamento: {e}")
        import traceback

        traceback.print_exc()
        if pegar_screenshot:
            return [], None
        else:
            return []


def salvar_mapa_atual(dados, url, descricao=None):
    try:
        from database import salvar_mapa

        mapa = salvar_mapa(dados, url, descricao)
        return mapa
    except Exception as e:
        print(f"⚠️ Não foi possível salvar no banco: {e}")
        return None
