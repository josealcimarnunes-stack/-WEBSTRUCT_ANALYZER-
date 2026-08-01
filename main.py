import webbrowser
import threading
import time
import config
from bootstrap import preparar_ambiente
from app import create_app


def abrir_navegador():
    time.sleep(1.5)
    webbrowser.open(f"http://{config.HOST}:{config.PORT}")


if __name__ == "__main__":
    # 1. Executa checagem de Hardware ID, Licença e Chrome
    preparar_ambiente()

    # 2. Cria a instância do Flask
    app = create_app()

    # 3. Abre o navegador nativo na Dashboard
    threading.Thread(target=abrir_navegador, daemon=True).start()

    # 4. Inicia o servidor local
    print(f"[*] Servidor rodando em http://{config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=False)
