from flask import Blueprint, jsonify, request
from database.repository import listar_seletores_salvos, verificar_status_seletor

selectors_bp = Blueprint("selectors", __name__)


@selectors_bp.route("/seletores/listar", methods=["GET"])
def listar_seletores():
    try:
        seletores = listar_seletores_salvos()
        resultado = [
            {
                "id": s.id,
                "nome": s.nome,
                "url": s.url,
                "seletor": s.seletor,
                "ultimo_status": s.ultimo_status,
            }
            for s in seletores
        ]
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@selectors_bp.route("/seletores/verificar", methods=["POST"])
def verificar_seletor():
    try:
        data = request.get_json() or {}
        seletor_id = data.get("id")
        url = data.get("url")
        seletor = data.get("seletor")

        valido = verificar_status_seletor(seletor_id, url, seletor)
        return jsonify({"valido": valido}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
