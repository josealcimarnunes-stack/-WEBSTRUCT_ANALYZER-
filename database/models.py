from database.connection import db
from datetime import datetime


class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class Mapa(db.Model):
    __tablename__ = "mapas"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    url = db.Column(db.Text, nullable=False)
    seletor_alvo = db.Column(db.String(255))
    total_elementos = db.Column(db.Integer)
    estrategia_usada = db.Column(db.String(100))
    screenshot_base64 = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    elementos = db.relationship(
        "Elemento", backref="mapa", cascade="all, delete-orphan"
    )


class Elemento(db.Model):
    __tablename__ = "elementos"
    id = db.Column(db.Integer, primary_key=True)
    mapa_id = db.Column(db.Integer, db.ForeignKey("mapas.id"), nullable=False)
    posicao = db.Column(db.Integer, nullable=False)
    tag_name = db.Column(db.String(50), nullable=False)
    element_id = db.Column(db.String(255))
    element_class = db.Column(db.Text)
    text_content = db.Column(db.Text)
    css_selector = db.Column(db.Text, nullable=False)
    xpath_selector = db.Column(db.Text, nullable=False)


class SeletorSalvo(db.Model):
    __tablename__ = "seletores_salvos"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    nome = db.Column(db.String(150), nullable=False)
    url = db.Column(db.Text, nullable=False)
    seletor = db.Column(db.Text, nullable=False)
    ultimo_status = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
