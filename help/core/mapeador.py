from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time
import base64
import json
import platform

# ⭐ CONFIGURAÇÕES DE TIMEOUT GLOBAIS ⭐
os.environ["PLAYWRIGHT_TIMEOUT"] = "300000"
os.environ["PLAYWRIGHT_WS_TIMEOUT"] = "300000"

TIMEOUT_PAGINA = 120000
TIMEOUT_NAVEGADOR = 60000


# ============================================
# ⭐ FUNÇÃO PARA ENCONTRAR PERFIL DO CHROME ⭐
# ============================================


def encontrar_perfil_chrome():
    """Procura o perfil do Chrome em vários lugares"""
    sistema = platform.system()
    usuario = os.path.expanduser("~")

    caminhos = {
        "Windows": [
            os.path.join(usuario, "AppData", "Local", "Google", "Chrome", "User Data"),
            os.path.join(usuario, "AppData", "Local", "Chromium", "User Data"),
        ],
        "Linux": [
            os.path.join(usuario, ".config", "google-chrome"),
            os.path.join(usuario, ".config", "chromium"),
        ],
        "Darwin": [
            os.path.join(usuario, "Library", "Application Support", "Google", "Chrome"),
            os.path.join(usuario, "Library", "Application Support", "Chromium"),
        ],
    }

    for caminho in caminhos.get(sistema, []):
        if os.path.exists(caminho):
            print(f"✅ Perfil do Chrome encontrado em: {caminho}")
            return caminho

    print("⚠️ Perfil do Chrome NÃO encontrado! Usando modo anônimo.")
    return None


def verificar_modo_anonimo():
    """Verifica se o sistema está em modo anônimo"""
    return encontrar_perfil_chrome() is None


# ⭐ DETECTA O SISTEMA OPERACIONAL ⭐
def get_chrome_path():
    sistema = platform.system()
    if sistema == "Windows":
        caminhos = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ]
        for caminho in caminhos:
            if os.path.exists(caminho):
                print(f"✅ Chrome encontrado em: {caminho}")
                return caminho
        print("❌ Chrome NÃO encontrado no Windows!")
        return None
    else:
        caminhos = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium-browser",
            "/usr/bin/google-chrome",
            "/usr/bin/chrome",
        ]
        for caminho in caminhos:
            if os.path.exists(caminho):
                print(f"✅ Chrome encontrado em: {caminho}")
                return caminho
        print("❌ Chrome NÃO encontrado no Linux!")
        return None


CAMINHO_CHROME = get_chrome_path()


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


def tirar_foto_rapida(url):
    print(f"📸 Tirando foto rápida de: {url}")
    try:
        with sync_playwright() as p:
            launch_options = {
                "headless": True,
                "timeout": TIMEOUT_NAVEGADOR,
                "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
            }
            if CAMINHO_CHROME:
                launch_options["executable_path"] = CAMINHO_CHROME
                print(f"✅ Usando Chrome em: {CAMINHO_CHROME}")

            browser = p.chromium.launch(**launch_options)
            page = browser.new_page()
            page.goto(url, timeout=60000, wait_until="networkidle")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.3)")
            page.wait_for_timeout(1000)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
            screenshot = page.screenshot(full_page=False)
            screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
            browser.close()
            print("📸 Foto rápida capturada com sucesso!")
            return screenshot_base64
    except Exception as e:
        print(f"❌ Erro ao tirar foto rápida: {e}")
        return None


# ============================================
# ⭐ FUNÇÃO DE MAPEAMENTO COM PROGRESSO ⭐
# ============================================


def analisar_estrutura_com_progresso(url):
    print(f"🔍 Analisando: {url}")
    try:
        with sync_playwright() as p:
            launch_options = {
                "headless": True,
                "timeout": TIMEOUT_NAVEGADOR,
                "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"],
            }
            if CAMINHO_CHROME:
                launch_options["executable_path"] = CAMINHO_CHROME
                print(f"✅ Usando Chrome em: {CAMINHO_CHROME}")

            browser = p.chromium.launch(**launch_options)
            page = browser.new_page()
            page.goto(url, timeout=120000, wait_until="networkidle")
            page.wait_for_selector("body", timeout=15000)
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
            browser.close()
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
            launch_options = {
                "headless": headless,
                "timeout": TIMEOUT_NAVEGADOR,
                "args": [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--disable-web-security",
                    "--disable-features=BlockInsecurePrivateNetworkRequests",
                ],
            }

            if headless and CAMINHO_CHROME:
                launch_options["executable_path"] = CAMINHO_CHROME
                print(f"✅ Usando Chrome do sistema (headless)")
            else:
                print("🪟 Usando Chromium do Playwright (VISÍVEL)")

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
