from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os
from auth import hash_senha, verificar_senha

# ⭐ CONFIGURAÇÃO DO BANCO ⭐
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data/mapas.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

os.makedirs("data", exist_ok=True)

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# ============================================
# ⭐ FUNÇÃO AUXILIAR ⭐
# ============================================


def para_string(valor):
    if valor is None:
        return ""
    if isinstance(valor, dict):
        return ""
    if isinstance(valor, list):
        return " ".join(str(v) for v in valor)
    if isinstance(valor, bool):
        return "1" if valor else "0"
    return str(valor)


# ============================================
# ⭐ MODELO DE USUÁRIO (NOVO) ⭐
# ============================================


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    senha_hash = Column(String(200), nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)
    ultimo_login = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "data_criacao": self.data_criacao.strftime("%Y-%m-%d %H:%M:%S"),
            "ultimo_login": (
                self.ultimo_login.strftime("%Y-%m-%d %H:%M:%S")
                if self.ultimo_login
                else None
            ),
        }


# ============================================
# ⭐ MODELO DE COOKIES (NOVO) ⭐
# ============================================


class CookieUsuario(Base):
    __tablename__ = "cookies_usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    site = Column(String(500), nullable=False)
    cookies_json = Column(Text, nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario")

    def to_dict(self):
        return {
            "id": self.id,
            "site": self.site,
            "cookies": json.loads(self.cookies_json),
            "data_criacao": self.data_criacao.strftime("%Y-%m-%d %H:%M:%S"),
        }


# ============================================
# ⭐ MODELO DE ATIVIDADES (NOVO) ⭐
# ============================================


class Atividade(Base):
    __tablename__ = "atividades"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    acao = Column(String(100), nullable=False)
    detalhe = Column(String(500), nullable=True)
    data = Column(DateTime, default=datetime.now)

    usuario = relationship("Usuario")


# ============================================
# ⭐ MODELOS EXISTENTES ⭐
# ============================================


class Mapa(Base):
    __tablename__ = "mapas"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False)
    data_mapeamento = Column(DateTime, default=datetime.now)
    total_elementos = Column(Integer, default=0)
    versao = Column(String(50), default="1.0")
    descricao = Column(String(200), nullable=True)

    elementos = relationship(
        "Elemento", back_populates="mapa", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "data_mapeamento": self.data_mapeamento.strftime("%Y-%m-%d %H:%M:%S"),
            "total_elementos": self.total_elementos,
            "versao": self.versao,
            "descricao": self.descricao,
            "elementos": [elem.to_dict() for elem in self.elementos],
        }


class Elemento(Base):
    __tablename__ = "elementos"

    id = Column(Integer, primary_key=True, index=True)
    mapa_id = Column(Integer, ForeignKey("mapas.id"), nullable=False)

    posicao = Column(Integer)
    profundidade = Column(Integer)
    tag = Column(String(50))
    classe = Column(String(200))
    elemento_id = Column(String(100))
    link = Column(String(500))
    texto = Column(Text)
    pai = Column(String(50))
    seletor_css = Column(String(500))
    xpath = Column(String(500))

    estavel = Column(Boolean, default=True)
    ultima_alteracao = Column(DateTime, nullable=True)

    mapa = relationship("Mapa", back_populates="elementos")

    def to_dict(self):
        return {
            "posicao": self.posicao,
            "profundidade": self.profundidade,
            "tag": self.tag,
            "classe": self.classe,
            "id": self.elemento_id,
            "link": self.link,
            "texto": self.texto,
            "pai": self.pai,
            "seletor_css": self.seletor_css,
            "xpath": self.xpath,
            "estavel": self.estavel,
        }


# ============================================
# ⭐ FUNÇÕES DE AUTENTICAÇÃO ⭐
# ============================================


def criar_usuario(nome, email, senha):
    session = SessionLocal()
    try:
        existente = session.query(Usuario).filter(Usuario.email == email).first()
        if existente:
            return False

        usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=hash_senha(senha),
        )
        session.add(usuario)
        session.commit()
        return True
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def verificar_usuario(email, senha):
    """Verifica as credenciais do usuário e retorna o ID ou None"""
    session = SessionLocal()
    try:
        usuario = session.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            return None

        if verificar_senha(senha, usuario.senha_hash):
            # ⭐ SALVA O ID E OS DADOS ANTES DE FECHAR A SESSÃO ⭐
            usuario_id = usuario.id
            usuario_nome = usuario.nome
            usuario_email = usuario.email

            # Atualiza o último login
            usuario.ultimo_login = datetime.now()
            session.commit()

            # ⭐ RETORNA OS DADOS EM UM DICIONÁRIO ⭐
            return {"id": usuario_id, "nome": usuario_nome, "email": usuario_email}

        return None
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")
        return None
    finally:
        session.close()


# ============================================
# ⭐ FUNÇÕES DE COOKIES ⭐
# ============================================


def salvar_cookies_usuario(usuario_id, site, cookies):
    session = SessionLocal()
    try:
        session.query(CookieUsuario).filter(
            CookieUsuario.usuario_id == usuario_id, CookieUsuario.site == site
        ).delete()

        cookie = CookieUsuario(
            usuario_id=usuario_id, site=site, cookies_json=json.dumps(cookies)
        )
        session.add(cookie)
        session.commit()
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar cookies: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def buscar_cookies_usuario(usuario_id, site):
    session = SessionLocal()
    try:
        cookie = (
            session.query(CookieUsuario)
            .filter(CookieUsuario.usuario_id == usuario_id, CookieUsuario.site == site)
            .order_by(CookieUsuario.data_criacao.desc())
            .first()
        )

        if cookie:
            return json.loads(cookie.cookies_json)
        return []
    except Exception as e:
        print(f"❌ Erro ao buscar cookies: {e}")
        return []
    finally:
        session.close()


# ============================================
# ⭐ FUNÇÕES DE ATIVIDADES ⭐
# ============================================


def registrar_atividade(usuario_id, acao, detalhe=None):
    session = SessionLocal()
    try:
        atividade = Atividade(
            usuario_id=usuario_id,
            acao=acao,
            detalhe=detalhe,
        )
        session.add(atividade)
        session.commit()
    except Exception as e:
        print(f"❌ Erro ao registrar atividade: {e}")
        session.rollback()
    finally:
        session.close()


# ============================================
# ⭐ FUNÇÕES EXISTENTES ⭐
# ============================================


def criar_tabelas():
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")


def salvar_mapa(dados, url, descricao=None):
    session = SessionLocal()
    try:
        mapa = Mapa(
            url=url,
            total_elementos=len(dados),
            descricao=descricao
            or f"Mapa gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        )
        session.add(mapa)
        session.flush()

        for elem in dados:
            elemento = Elemento(
                mapa_id=mapa.id,
                posicao=elem.get("posicao"),
                profundidade=elem.get("profundidade"),
                tag=para_string(elem.get("tag")),
                classe=para_string(elem.get("classe")),
                elemento_id=para_string(elem.get("id")),
                link=para_string(elem.get("link")),
                texto=para_string(elem.get("texto")),
                pai=para_string(elem.get("pai")),
                seletor_css=para_string(elem.get("seletor_css")),
                xpath=para_string(elem.get("xpath")),
                estavel=True,
            )
            session.add(elemento)

        session.commit()
        print(
            f"✅ Mapa salvo com sucesso! ID: {mapa.id} - {mapa.total_elementos} elementos"
        )
        return mapa
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao salvar mapa: {e}")
        import traceback

        traceback.print_exc()
        return None
    finally:
        session.close()


def buscar_ultimo_mapa(url):
    session = SessionLocal()
    try:
        mapa = (
            session.query(Mapa)
            .filter(Mapa.url == url)
            .order_by(Mapa.data_mapeamento.desc())
            .first()
        )
        return mapa
    except Exception as e:
        print(f"❌ Erro ao buscar mapa: {e}")
        return None
    finally:
        session.close()


def listar_mapas(url=None, limite=10):
    session = SessionLocal()
    try:
        query = session.query(Mapa)
        if url:
            query = query.filter(Mapa.url == url)
        mapas = query.order_by(Mapa.data_mapeamento.desc()).limit(limite).all()
        return [m.to_dict() for m in mapas]
    except Exception as e:
        print(f"❌ Erro ao listar mapas: {e}")
        return []
    finally:
        session.close()


def contar_mapas():
    session = SessionLocal()
    try:
        total = session.query(Mapa).count()
        return total
    except Exception as e:
        print(f"❌ Erro ao contar mapas: {e}")
        return 0
    finally:
        session.close()


def comparar_mapas(mapa_atual, mapa_anterior):
    if not mapa_anterior:
        return {"status": "primeiro_mapa", "mensagem": "Este é o primeiro mapa salvo."}

    elementos_antigos = {e.posicao: e for e in mapa_anterior.elementos}
    elementos_novos = {e.get("posicao"): e for e in mapa_atual}

    mudancas = {"iguais": [], "mudaram": [], "sumiram": [], "novos": []}

    for pos, elem in elementos_novos.items():
        if pos in elementos_antigos:
            antigo = elementos_antigos[pos]
            mudou = False
            campos_mudaram = []

            if antigo.seletor_css != elem.get("seletor_css"):
                mudou = True
                campos_mudaram.append("seletor_css")
            if antigo.xpath != elem.get("xpath"):
                mudou = True
                campos_mudaram.append("xpath")
            if antigo.texto != elem.get("texto"):
                mudou = True
                campos_mudaram.append("texto")

            if mudou:
                mudancas["mudaram"].append(
                    {
                        "posicao": pos,
                        "tag": elem.get("tag"),
                        "campos": campos_mudaram,
                        "antigo": {
                            "seletor_css": antigo.seletor_css,
                            "xpath": antigo.xpath,
                            "texto": antigo.texto,
                        },
                        "novo": {
                            "seletor_css": elem.get("seletor_css"),
                            "xpath": elem.get("xpath"),
                            "texto": elem.get("texto"),
                        },
                    }
                )
            else:
                mudancas["iguais"].append(pos)
        else:
            mudancas["novos"].append(elem)

    for pos, elem in elementos_antigos.items():
        if pos not in elementos_novos:
            mudancas["sumiram"].append(elem.posicao)

    return mudancas


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def contar_mapas_por_url(url):
    session = SessionLocal()
    try:
        total = session.query(Mapa).filter(Mapa.url == url).count()
        return total
    except Exception as e:
        print(f"❌ Erro ao contar mapas: {e}")
        return 0
    finally:
        session.close()
