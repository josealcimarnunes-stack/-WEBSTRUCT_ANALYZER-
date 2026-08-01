from flask import Blueprint, render_template, request, jsonify
from core.mapeador import (
    iniciar_sessao_guiada,
    mapear_pagina_atual,
    interagir_elemento,
    fechar_sessao,
)

scraping_bp = Blueprint("scraping", __name__)


@scraping_bp.route("/")
def index():
    return render_template("index.html")


@scraping_bp.route("/iniciar_sessao", methods=["POST"])
def iniciar_sessao():
    try:
        data = request.get_json() or {}
        url = data.get("url")
        if not url:
            return jsonify({"erro": "Por favor, informe a URL do site."}), 400

        # Garante o fechamento seguro de qualquer sessão anterior antes de abrir a nova
        try:
            fechar_sessao()
        except Exception:
            pass

        iniciar_sessao_guiada(url)
        return (
            jsonify(
                {
                    "sucesso": True,
                    "mensagem": "Sessão iniciada com sucesso. Sessão anterior encerrada.",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@scraping_bp.route("/mapear", methods=["POST"])
def mapear():
    try:
        data = request.get_json() or {}
        seletor_alvo = data.get("seletor_alvo", "")

        res = mapear_pagina_atual(seletor_alvo)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@scraping_bp.route("/interagir", methods=["POST"])
def interagir():
    try:
        data = request.get_json() or {}
        seletor = data.get("seletor")
        acao = data.get("acao")
        valor = data.get("valor", "")

        if not seletor or not acao:
            return jsonify({"erro": "Seletor e ação são obrigatórios."}), 400

        res = interagir_elemento(seletor, acao, valor)
        return jsonify(res), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


@scraping_bp.route("/fechar_sessao", methods=["POST"])
def fechar():
    try:
        fechar_sessao()
        return (
            jsonify({"sucesso": True, "mensagem": "Sessão encerrada com sucesso."}),
            200,
        )
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
