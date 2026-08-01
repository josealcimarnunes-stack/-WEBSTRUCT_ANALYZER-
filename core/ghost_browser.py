import time
import random

SCRIPT_GHOST_BYPASS = """
() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.chrome = { runtime: {} };
    Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
}
"""


def simular_comportamento_humano(page):
    """Simula interações de mouse e rolagem suave na página."""
    try:
        page.evaluate(SCRIPT_GHOST_BYPASS)
        viewport = page.viewport_size or {"width": 1366, "height": 768}

        for _ in range(random.randint(2, 4)):
            x = random.randint(100, viewport["width"] - 100)
            y = random.randint(100, viewport["height"] - 100)
            page.mouse.move(x, y, steps=10)
            time.sleep(random.uniform(0.1, 0.3))

        page.evaluate("window.scrollBy({ top: 300, behavior: 'smooth' });")
        time.sleep(0.5)
    except Exception as e:
        print(f"[!] Erro no Ghost Browser: {e}")
