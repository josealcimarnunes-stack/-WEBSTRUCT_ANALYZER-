"""
ESTRATÉGIAS DE MAPEAMENTO PARA SITES COM ANTI-BOT
Vai tentando do mais leve pro mais pesado!
"""

from playwright.sync_api import sync_playwright
import time
import os


# ============================================
# ⭐ ESTRATÉGIA 1: HEADLESS (MAIS LEVE)
# ============================================
def estrategia_headless(url):
    print("🔇 [1] Tentando em modo headless (invisível)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
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
# ⭐ ESTRATÉGIA 2: NORMAL (JANELA VISÍVEL)
# ============================================
def estrategia_normal(url):
    print("🪟 [2] Abrindo navegador visível...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        page = browser.new_page()
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
# ⭐ ESTRATÉGIA 3: STEALTH (ESCONDE QUE É BOT)
# ============================================
def estrategia_stealth(url):
    print("🕵️ [3] Tentando esconder que é bot...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

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
# ⭐ ESTRATÉGIA 4: FINGERPRINT REAL (MAIS PESADA)
# ============================================
def estrategia_fingerprint(url):
    print("🎭 [4] Simulando usuário real completo...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )

        page = browser.new_page(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="pt-BR",
            timezone_id="America/Sao_Paulo",
        )

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
# ⭐ FUNÇÃO PRINCIPAL (CIRÚRGICA)
# ============================================
def analisar_com_todas_estrategias(url):
    print("\n" + "=" * 60)
    print(f"🎯 MAPEANDO: {url}")
    print("=" * 60 + "\n")

    # ⭐ LISTA DE ESTRATÉGIAS (DA MAIS LEVE PRA MAIS PESADA) ⭐
    estrategias = [
        estrategia_headless,  # 1º: Rápido, invisível
        estrategia_normal,  # 2º: Visível, normal
        estrategia_stealth,  # 3º: Esconde que é bot
        estrategia_fingerprint,  # 4º: Simula usuário real
    ]

    for func in estrategias:
        try:
            elementos = func(url)
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
