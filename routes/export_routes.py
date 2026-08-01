import csv
import io
import json
from flask import Blueprint, Response, jsonify
from database.repository import buscar_mapa_por_id

export_bp = Blueprint("export", __name__)


@export_bp.route("/exportar/<string:formato>/<int:mapa_id>", methods=["GET"])
def exportar(formato, mapa_id):
    mapa = buscar_mapa_por_id(mapa_id)
    if not mapa:
        return jsonify({"erro": "Mapa não encontrado"}), 404

    dados = [
        {
            "Posicao": e.posicao,
            "Tag": e.tag_name,
            "ID": e.element_id,
            "Classe": e.element_class,
            "Texto": e.text_content,
            "CSS Selector": e.css_selector,
            "XPath": e.xpath_selector,
        }
        for e in mapa.elementos
    ]

    if formato == "json":
        return Response(
            json.dumps(dados, indent=2, ensure_ascii=False),
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment;filename=mapa_{mapa_id}.json"},
        )

    elif formato == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=dados[0].keys() if dados else [])
        writer.writeheader()
        writer.writerows(dados)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename=mapa_{mapa_id}.csv"},
        )

    return jsonify({"erro": "Formato não suportado"}), 400
