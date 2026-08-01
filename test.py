import time
import json
from playwright.sync_api import sync_playwright


def escutar_rede_carteiro(
    url_alvo="https://www.mercadolivre.com.br/",
):
    print(f"🕵️‍♂️ Iniciando radar de tráfego (Filtro Sniper) em: {url_alvo}")

    # Termos sigilosos para proteger dados sensíveis
    termos_sigilosos = [
        "auth",
        "password",
        "login",
        "credit",
        "checkout",
        "token",
        "session",
    ]

    # Domínios/Termos de telemetria/métricas para ignorar (ruído)
    termos_ruido = [
        "melidata",
        "web-monitoring",
        "analytics",
        "google-analytics",
        "facebook",
        "viewability",
    ]

    pacotes_json_uteis = []
    contador_sigilosos = 0
    contador_ruido_ignorado = 0

    with sync_playwright() as p:
        # Abrindo o navegador
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context()
        page = context.new_page()

        # Interceptador focado SOMENTE em JSONs úteis
        def handle_response(response):
            nonlocal contador_sigilosos, contador_ruido_ignorado
            url = response.url.lower()

            # 1. Proteção: Ignora URLs com dados sensíveis
            if any(termo in url for termo in termos_sigilosos):
                contador_sigilosos += 1
                return

            # 2. Limpeza: Ignora rotas conhecidas de telemetria/métricas
            if any(ruido in url for ruido in termos_ruido):
                contador_ruido_ignorado += 1
                return

            try:
                content_type = response.headers.get("content-type", "").lower()

                # 🎯 O PONTO CHAVE: Só entra se for explicitamente JSON!
                # Ignora text/css, text/javascript, text/html, imagens, etc.
                if "application/json" in content_type:
                    # Pega o JSON já convertido em dicionário
                    dados_json = response.json()

                    pacotes_json_uteis.append(
                        {
                            "url": response.url,
                            "content_type": content_type,
                            "conteudo_json": dados_json,
                        }
                    )
            except Exception:
                # Se não for um JSON válido ou falhar ao ler o body, descarta
                pass

        # Ativa o radar de respostas
        page.on("response", handle_response)

        try:
            print("🌐 Navegando e escutando as requisições de API...")
            page.goto(url_alvo, timeout=60000)

            # Rola a página para baixo para forçar requisições assíncronas (Lazy Loading)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(5)

        except Exception as e:
            print(f"❌ Erro na navegação: {e}")
        finally:
            print("\n" + "=" * 60)
            print("📊 RELATÓRIO DO RADAR SNIPER DE REDE:")
            print(f"🔒 Pacotes sigilosos protegidos: {contador_sigilosos}")
            print(
                f"🗑️ Ruídos de métricas/telemetria ignorados: {contador_ruido_ignorado}"
            )
            print(
                f"🎯 PACOTES JSON LIMPOS E ÚTEIS CAPTURADOS: {len(pacotes_json_uteis)}"
            )
            print("=" * 60)

            output_filename = "carteiros_json_limpos.txt"
            print(f"📝 Gerando relatório sem ruído: {output_filename}...")

            with open(output_filename, "w", encoding="utf-8") as f:
                f.write("=== RELATÓRIO DE PACAOTES DE DADOS (JSON APENAS) ===\n")
                f.write(f"URL Alvo: {url_alvo}\n")
                f.write(
                    f"Total de JSONs Limpos Capturados: {len(pacotes_json_uteis)}\n\n"
                )

                for idx, pacote in enumerate(pacotes_json_uteis, 1):
                    f.write(f"================ PACOTE JSON #{idx} ================\n")
                    f.write(f"URL DA REQUISIÇÃO: {pacote['url']}\n")
                    f.write(f"TIPO: {pacote['content_type']}\n")
                    f.write("CONTEÚDO DA BOLSA (DADOS ESTRUTURADOS):\n")

                    # Converte o JSON do Python em texto legível e identado
                    json_formatado = json.dumps(
                        pacote["conteudo_json"], indent=4, ensure_ascii=False
                    )
                    f.write(json_formatado + "\n\n")

            print(
                f"✅ Sucesso! Abra o arquivo '{output_filename}' para ver o ouro limpo!"
            )
            browser.close()


if __name__ == "__main__":
    escutar_rede_carteiro("https://www.mercadolivre.com.br/")
