import time
from playwright.sync_api import sync_playwright
import config

_playwright_instance = None
_browser_instance = None
_page_instance = None


def iniciar_sessao_guiada(url):
    global _playwright_instance, _browser_instance, _page_instance

    # Garante que qualquer sessão anterior seja encerrada antes de abrir a nova
    fechar_sessao()

    _playwright_instance = sync_playwright().start()

    # Usa o perfil persistente configurado em config.py
    _browser_instance = _playwright_instance.chromium.launch_persistent_context(
        user_data_dir=str(config.CHROME_PROFILE_DIR),
        headless=False,
        args=["--start-maximized"],
    )

    if _browser_instance.pages:
        _page_instance = _browser_instance.pages[0]
    else:
        _page_instance = _browser_instance.new_page()

    _page_instance.goto(url)
    time.sleep(2)


def mapear_pagina_atual(seletor_alvo=""):
    global _page_instance
    if not _page_instance:
        raise Exception(
            "Nenhuma sessão de navegador ativa. Inicie uma sessão primeiro."
        )

    # Se um seletor específico foi passado, busca ele; caso contrário, busca elementos comuns
    query = seletor_alvo if seletor_alvo else "body *"

    elementos_encontrados = []
    try:
        locators = _page_instance.locator(query).all()
        for index, loc in enumerate(
            locators[:50]
        ):  # Limita aos primeiros 50 para performance
            try:
                tag = loc.evaluate("el => el.tagName.toLowerCase()")
                el_id = loc.get_attribute("id") or ""
                el_class = loc.get_attribute("class") or ""
                text = loc.inner_text().strip().replace("\n", " ")[:100]

                elementos_encontrados.append(
                    {
                        "posicao": index + 1,
                        "tag_name": tag,
                        "id": el_id,
                        "class": el_class,
                        "text": text,
                        "css_selector": query,
                        "xpath": f"//{tag}",
                    }
                )
            except Exception:
                continue
    except Exception as e:
        print(f"    ⚠️ Erro ao varrer elementos: {e}")

    return {"total": len(elementos_encontrados), "elementos": elementos_encontrados}


def interagir_elemento(seletor, acao, valor=""):
    global _page_instance
    if not _page_instance:
        raise Exception("Nenhuma sessão de navegador ativa.")

    locator = _page_instance.locator(seletor).first
    if acao == "clicar":
        locator.click()
    elif acao == "preencher":
        locator.fill(valor)

    return {
        "sucesso": True,
        "mensagem": f"Ação '{acao}' executada no seletor '{seletor}'.",
    }


def fechar_sessao():
    global _playwright_instance, _browser_instance, _page_instance
    try:
        if _browser_instance:
            _browser_instance.close()
        if _playwright_instance:
            _playwright_instance.stop()
    except Exception:
        pass
    finally:
        _browser_instance = None
        _playwright_instance = None
        _page_instance = None
