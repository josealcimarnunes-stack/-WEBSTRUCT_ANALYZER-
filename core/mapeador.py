from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os
import time
import base64
import json
import platform

# ⭐ CONFIGURAÇÕES DE TIMEOUT GLOBAIS ⭐
os.environ["PLAYWRIGHT_TIMEOUT"] = "300000"  # 5 minutos
os.environ["PLAYWRIGHT_WS_TIMEOUT"] = "300000"  # 5 minutos

TIMEOUT_PAGINA = 120000  # 2 minutos para carregar a página
TIMEOUT_NAVEGADOR = 60000  # 1 minuto para iniciar o navegador


# ⭐ DETECTA O SISTEMA OPERACIONAL E AJUSTA O CAMINHO DO CHROME ⭐
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
        print("❌ Chrome NÃO encontrado no Windows! Tentando baixar...")
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
        print("❌ Chrome NÃO encontrado no Linux! Tentando baixar...")
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
# ⭐ FUNÇÃO PARA TIRAR FOTO RÁPIDA (CORRIGIDA) ⭐
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
# ⭐ FUNÇÃO DE MAPEAMENTO COM PROGRESSO (CORRIGIDA) ⭐
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
            print(f"🔍 Total de elementos encontrados via evaluate: {len(elementos)}")

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
# ⭐ FUNÇÃO DE MAPEAMENTO COMPLETO (CORRIGIDA) ⭐
# ============================================


def analisar_estrutura(url, pegar_screenshot=False, headless=True):
    print(f"🔍 Analisando: {url}")
    dados = []
    screenshot_base64 = None
    try:
        with sync_playwright() as p:
            launch_options = {
                "headless": headless,  # ⭐ AGORA USA O PARÂMETRO
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

            if pegar_screenshot:
                page.wait_for_timeout(2000)
                screenshot = page.screenshot(full_page=True)
                screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
                print("📸 Screenshot capturado!")

            print("⏳ Rolando a página para carregar conteúdo dinâmico...")
            for _ in range(5):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)

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
            print(f"🔍 Total de elementos encontrados via evaluate: {len(elementos)}")

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

            print(f"✅ {len(dados)} elementos mapeados!")
            browser.close()
            print("✅ Processo concluído!")

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


def analisar_estrutura_com_fallback(url):
    # Tenta em modo headless primeiro
    try:
        print("🔍 Tentando mapear em modo headless...")
        dados = analisar_estrutura(url, headless=True)
        if dados:
            print(f"✅ Mapeamento headless concluído! {len(dados)} elementos")
            return dados
        else:
            raise Exception("Nenhum dado retornado do headless")
    except Exception as e:
        print(f"⚠️ Erro no headless: {e}")
        print("🪟 Tentando com janela aberta...")
        dados = analisar_estrutura(url, headless=False)
        if dados:
            print(f"✅ Mapeamento com janela concluído! {len(dados)} elementos")
            return dados
        else:
            print("❌ Falha no mapeamento com janela também!")
            return []
