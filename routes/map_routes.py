from flask import Blueprint, jsonify, request
from database.repository import (
    listar_mapas_historico,
    buscar_mapa_por_id,
    comparar_mapas_diff,
)

map_bp = Blueprint("map", __name__)


@map_bp.route("/mapas/historico", methods=["GET"])
def historico():
    mapas = listar_mapas_historico()
    resultado = [
        {
            "id": m.id,
            "url": m.url,
            "seletor_alvo": m.seletor_alvo,
            "total_elementos": m.total_elementos,
            "criado_em": m.criado_em.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for m in mapas
    ]
    return jsonify(resultado)


@map_bp.route("/mapas/<int:mapa_id>", methods=["GET"])
def buscar_mapa(mapa_id):
    mapa = buscar_mapa_por_id(mapa_id)
    if not mapa:
        return jsonify({"erro": "Mapa não encontrado"}), 404

    elementos = [
        {
            "posicao": e.posicao,
            "tag_name": e.tag_name,
            "id": e.element_id,
            "class": e.element_class,
            "text": e.text_content,
            "css_selector": e.css_selector,
            "xpath": e.xpath_selector,
        }
        for e in mapa.elementos
    ]

    return jsonify(
        {
            "id": mapa.id,
            "url": mapa.url,
            "seletor_alvo": mapa.seletor_alvo,
            "screenshot": mapa.screenshot_base64,
            "elementos": elementos,
        }
    )


@map_bp.route("/mapas/comparar", methods=["POST"])
def comparar():
    data = request.json or {}
    antigo_id = data.get("antigo_id")
    novo_id = data.get("novo_id")

    diff = comparar_mapas_diff(antigo_id, novo_id)
    if not diff:
        return jsonify({"erro": "Falha ao comparar os mapas especificados."}), 400

    return jsonify(diff)
