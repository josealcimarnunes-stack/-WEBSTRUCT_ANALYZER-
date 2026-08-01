import time
from core.mapeador import mapear_pagina_atual


def analisar_com_todas_estrategias(url, seletor_alvo):
    """
    Tenta mapear com fallbacks sucessivos caso encontre resistências ou poucos elementos.
    """
    estrategias = ["Headless", "Normal", "Stealth", "Fingerprint"]

    for estrategia in estrategias:
        try:
            resultado = mapear_pagina_atual(seletor_alvo)
            if resultado and resultado.get("total", 0) > 0:
                resultado["estrategia_usada"] = estrategia
                return resultado
        except Exception as e:
            print(f"[!] Falha na estratégia {estrategia}: {e}")
            continue

    raise Exception(
        "Não foi possível extrair elementos usando nenhuma das estratégias ativas."
    )
