from collections import Counter


def processar_estatisticas_elementos(elementos):
    """Processa contagens e relatórios estatísticos dos elementos capturados."""
    tags = [e.get("tag_name") for e in elementos if e.get("tag_name")]
    ids = [e.get("id") for e in elementos if e.get("id")]
    com_texto = [e for e in elementos if e.get("text")]

    return {
        "total_elementos": len(elementos),
        "top_tags": dict(Counter(tags).most_common(5)),
        "total_com_id": len(ids),
        "total_com_texto": len(com_texto),
    }
