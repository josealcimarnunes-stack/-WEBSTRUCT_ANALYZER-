from database.connection import db
from database.models import Usuario, Mapa, Elemento, SeletorSalvo
from datetime import datetime


def buscar_usuario_por_name(username):
    return Usuario.query.filter_by(username=username).first()


def criar_usuario(username, password_hash):
    novo_usuario = Usuario(
        username=username, password_hash=password_hash, criado_em=datetime.utcnow()
    )
    db.session.add(novo_usuario)
    db.session.commit()
    return novo_usuario


def listar_mapas_historico():
    return Mapa.query.order_by(Mapa.criado_em.desc()).all()


def buscar_mapa_por_id(mapa_id):
    return Mapa.query.get(mapa_id)


def listar_seletores_salvos():
    return SeletorSalvo.query.order_by(SeletorSalvo.criado_em.desc()).all()


def verificar_status_seletor(seletor_id, url, seletor):
    seletor_obj = SeletorSalvo.query.get(seletor_id)
    if not seletor_obj:
        return False
    valido = True
    seletor_obj.ultimo_status = valido
    seletor_obj.atualizado_em = datetime.utcnow()
    db.session.commit()
    return valido


def comparar_mapas_diff(mapa_id_1, mapa_id_2):
    """Compara dois mapas salvos para retornar as diferenças estruturais."""
    mapa1 = Mapa.query.get(mapa_id_1)
    mapa2 = Mapa.query.get(mapa_id_2)

    if not mapa1 or not mapa2:
        raise Exception("Um ou ambos os mapas não foram encontrados para comparação.")

    elementos_1 = {el.css_selector for el in mapa1.elementos}
    elementos_2 = {el.css_selector for el in mapa2.elementos}

    adicionados = list(elementos_2 - elementos_1)
    removidos = list(elementos_1 - elementos_2)

    return {
        "mapa_1_id": mapa1.id,
        "mapa_2_id": mapa2.id,
        "adicionados": adicionados,
        "removidos": removidos,
        "total_diferencas": len(adicionados) + len(removidos),
    }
