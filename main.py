import os
import sys
import webbrowser
import threading
import time
import subprocess
import json

from flask import (
    Flask,
    Response,
    session,
    redirect,
    url_for,
    request,
    render_template,
    jsonify,
    send_file,
)

import pandas as pd
import io
from collections import Counter
import traceback
from functools import wraps

# ⭐ CONFIGURAÇÃO DO BANCO ⭐
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data/mapas.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ⭐ CRIA O APP ⭐
app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "webstruct-secret-key-change-in-production"
)


def configurar_playwright():
    if getattr(sys, "frozen", False):
        browsers_path = os.path.join(sys._MEIPASS, "playwright_browsers")
        if os.path.exists(browsers_path):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
            print(f"✅ Navegadores configurados em: {browsers_path}")
        else:
            print("⚠️ Navegadores não encontrados no .exe")
    else:
        browsers_path = os.path.join(os.getcwd(), "playwright_browsers")
        if os.path.exists(browsers_path):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path
            print(f"✅ Navegadores configurados em: {browsers_path}")


configurar_playwright()

# ⭐ IMPORTA DA PASTA CORE ⭐
from core.mapeador import (
    analisar_estrutura,
    salvar_mapa_atual,
    tirar_foto_rapida,
    analisar_estrutura_com_progresso,
    verificar_modo_anonimo,
)
from core.processador import processar_estrutura
from core.gerador_codigo import gerar_codigo

from database import (
    criar_tabelas,
    salvar_mapa,
    buscar_ultimo_mapa,
    listar_mapas,
    comparar_mapas,
    contar_mapas,
    contar_mapas_por_url,
    SessionLocal,
    Mapa,
    Usuario,
    verificar_usuario,
    criar_usuario,
    salvar_cookies_usuario,
    buscar_cookies_usuario,
    registrar_atividade,
)

# ⭐ CRIA AS TABELAS ⭐
criar_tabelas()

# ⭐ CACHE DO MAPA ⭐
cache_mapa = {"dados": [], "url": "", "total": 0}


# ============================================
# ⭐ DECORADOR PARA ROTAS PROTEGIDAS ⭐
# ============================================


def login_obrigatorio(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# ============================================
# ⭐ ROTAS DE AUTENTICAÇÃO ⭐
# ============================================


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario_data = verificar_usuario(email, senha)  # ⭐ AGORA É UM DICIONÁRIO
        if usuario_data:
            session["usuario_id"] = usuario_data["id"]  # ✅ PEGA DO DICIONÁRIO
            session["usuario_email"] = usuario_data["email"]
            session["usuario_nome"] = usuario_data["nome"]
            registrar_atividade(usuario_data["id"], "login", "Login realizado")
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", erro="Email ou senha inválidos!")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        confirmar = request.form.get("confirmar")

        if senha != confirmar:
            return render_template("register.html", erro="As senhas não coincidem!")

        if criar_usuario(nome, email, senha):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", erro="Email já cadastrado!")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ============================================
# ⭐ ROTA PRINCIPAL (PROTEGIDA) ⭐
# ============================================


@app.route("/")
@login_obrigatorio
def dashboard():
    return render_template("dashboard.html", usuario=session.get("usuario_nome"))


# ============================================
# ⭐ ROTA PARA MAPEAR COM ESTRATÉGIAS ⭐
# ============================================


@app.route("/mapear_com_estrategias", methods=["POST"])
@login_obrigatorio
def mapear_com_estrategias():
    url = request.json.get("url", "")
    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400

    try:
        from estrategias import analisar_com_todas_estrategias

        print(f"🧠 Mapeando com estratégias: {url}")

        usuario_id = session.get("usuario_id")
        cookies = buscar_cookies_usuario(usuario_id, url)

        dados = analisar_com_todas_estrategias(url, cookies)

        if dados and len(dados) > 50:
            global cache_mapa
            cache_mapa["dados"] = dados
            cache_mapa["url"] = url
            cache_mapa["total"] = len(dados)

            registrar_atividade(usuario_id, "mapear", url)

            return jsonify(
                {
                    "sucesso": True,
                    "total": len(dados),
                    "mensagem": f"✅ {len(dados)} elementos mapeados!",
                }
            )
        else:
            return jsonify({"erro": "Não foi possível mapear o site"}), 500

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500


# ============================================
# ⭐ ROTA PARA SALVAR COOKIES ⭐
# ============================================


@app.route("/salvar_cookies", methods=["POST"])
@login_obrigatorio
def salvar_cookies():
    site = request.json.get("site")
    cookies = request.json.get("cookies")

    if not site or not cookies:
        return jsonify({"erro": "Dados incompletos"}), 400

    usuario_id = session.get("usuario_id")
    salvar_cookies_usuario(usuario_id, site, cookies)
    registrar_atividade(usuario_id, "salvar_cookies", site)

    return jsonify({"sucesso": True})


# ============================================
# ⭐ ROTA PARA VERIFICAR MODO ANÔNIMO ⭐
# ============================================


@app.route("/verificar_modo", methods=["GET"])
@login_obrigatorio
def verificar_modo():
    anonimo = verificar_modo_anonimo()
    return jsonify(
        {
            "anonimo": anonimo,
            "mensagem": (
                "⚠️ Modo anônimo detectado! A eficácia pode ser reduzida."
                if anonimo
                else "✅ Perfil do Chrome encontrado!"
            ),
        }
    )


# ============================================
# ⭐ ROTAS EXISTENTES ⭐
# ============================================


@app.route("/previa_rapida", methods=["POST"])
@login_obrigatorio
def previa_rapida():
    url = request.json.get("url", "")
    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400
    try:
        screenshot = tirar_foto_rapida(url)
        if screenshot:
            return jsonify({"screenshot": screenshot})
        else:
            return jsonify({"erro": "Não foi possível capturar a foto"}), 500
    except Exception as e:
        print(f"❌ Erro ao capturar foto rápida: {e}")
        return jsonify({"erro": str(e)}), 500


@app.route("/mapear_progresso", methods=["GET"])
@login_obrigatorio
def mapear_progresso():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400

    def generate():
        global cache_mapa
        try:
            for progresso in analisar_estrutura_com_progresso(url):
                data = json.loads(progresso)
                if data.get("status") == "concluido":
                    cache_mapa["dados"] = data.get("dados", [])
                    cache_mapa["url"] = url
                    cache_mapa["total"] = len(cache_mapa["dados"])
                    print(f"✅ Cache atualizado: {cache_mapa['total']} elementos")
                yield f"data: {progresso}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'erro', 'mensagem': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")


@app.route("/mapear", methods=["POST"])
@login_obrigatorio
def mapear():
    global cache_mapa
    url = request.json.get("url", "")
    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400
    try:
        dados = analisar_estrutura(url)
        cache_mapa["dados"] = dados
        cache_mapa["url"] = url
        cache_mapa["total"] = len(dados)

        tags = Counter()
        classes = Counter()
        for elem in dados:
            tags[elem.get("tag", "desconhecido")] += 1
            if elem.get("classe"):
                for cls in elem["classe"].split():
                    classes[cls] += 1

        return jsonify(
            {
                "sucesso": True,
                "url": url,
                "total": len(dados),
                "tags": dict(tags.most_common(10)),
                "classes": dict(classes.most_common(5)),
                "todos": dados,
                "primeiros": dados[:10],
            }
        )
    except Exception as e:
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500


@app.route("/reiniciar_sistema", methods=["POST"])
@login_obrigatorio
def reiniciar_sistema_rota():
    global cache_mapa
    try:
        cache_mapa = {"dados": [], "url": "", "total": 0}
        print("🔄 Sistema reiniciado com sucesso!")
        return jsonify({"sucesso": True, "mensagem": "Sistema reiniciado!"})
    except Exception as e:
        print(f"❌ Erro ao reiniciar sistema: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500


@app.route("/salvar_mapa", methods=["POST"])
@login_obrigatorio
def salvar_mapa_rota():
    global cache_mapa
    if not cache_mapa["dados"]:
        return jsonify({"erro": "Nenhum mapa para salvar"}), 400

    dados = cache_mapa["dados"]
    url = cache_mapa["url"]
    descricao = request.json.get(
        "descricao", f"Mapa gerado em {time.strftime('%Y-%m-%d %H:%M')}"
    )

    mapa = salvar_mapa(dados, url, descricao)

    if mapa:
        usuario_id = session.get("usuario_id")
        registrar_atividade(usuario_id, "salvar_mapa", url)
        return jsonify(
            {
                "sucesso": True,
                "id": mapa.id,
                "total": mapa.total_elementos,
                "mensagem": f"Mapa salvo com sucesso! ID: {mapa.id}",
            }
        )
    else:
        return jsonify({"erro": "Erro ao salvar mapa"}), 500


@app.route("/listar_mapas", methods=["GET"])
@login_obrigatorio
def listar_mapas_rota():
    url = request.args.get("url")
    mapas = listar_mapas(url=url, limite=50)
    return jsonify({"mapas": mapas, "total": len(mapas)})


@app.route("/comparar_mapas", methods=["POST"])
@login_obrigatorio
def comparar_mapas_rota():
    global cache_mapa
    if not cache_mapa["dados"]:
        return jsonify({"erro": "Nenhum mapa atual para comparar"}), 400

    url = cache_mapa["url"]

    from database import SessionLocal, Mapa, Elemento

    session_db = SessionLocal()

    try:
        mapa_anterior = (
            session_db.query(Mapa)
            .filter(Mapa.url == url)
            .order_by(Mapa.data_mapeamento.desc())
            .first()
        )

        if not mapa_anterior:
            return jsonify(
                {
                    "status": "primeiro_mapa",
                    "mensagem": "Este é o primeiro mapa salvo para esta URL.",
                }
            )

        from database import comparar_mapas

        comparacao = comparar_mapas(cache_mapa["dados"], mapa_anterior)

        return jsonify(
            {
                "status": "comparado",
                "comparacao": comparacao,
                "mapa_anterior_id": mapa_anterior.id,
                "data_anterior": mapa_anterior.data_mapeamento.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "total_mudancas": len(comparacao["mudaram"]),
                "total_sumidos": len(comparacao["sumiram"]),
                "total_novos": len(comparacao["novos"]),
                "total_iguais": len(comparacao["iguais"]),
            }
        )

    except Exception as e:
        print(f"❌ Erro ao comparar mapas: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
    finally:
        session_db.close()


@app.route("/estatisticas_banco", methods=["GET"])
@login_obrigatorio
def estatisticas_banco():
    total = contar_mapas()
    return jsonify({"total_mapas": total})


@app.route("/verificar_mapa", methods=["GET"])
@login_obrigatorio
def verificar_mapa():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400

    mapa = buscar_ultimo_mapa(url)

    if mapa:
        return jsonify(
            {
                "existe": True,
                "id": mapa.id,
                "data": mapa.data_mapeamento.strftime("%Y-%m-%d %H:%M"),
                "total_elementos": mapa.total_elementos,
                "descricao": mapa.descricao,
                "total_mapas": contar_mapas_por_url(url),
            }
        )
    else:
        return jsonify({"existe": False})


@app.route("/carregar_mapa", methods=["GET"])
@login_obrigatorio
def carregar_mapa():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"erro": "URL não fornecida"}), 400

    session_db = SessionLocal()

    try:
        mapa = (
            session_db.query(Mapa)
            .filter(Mapa.url == url)
            .order_by(Mapa.data_mapeamento.desc())
            .first()
        )

        if not mapa:
            return jsonify({"erro": "Nenhum mapa encontrado"}), 404

        elementos_dict = []
        for elem in mapa.elementos:
            elementos_dict.append(
                {
                    "posicao": elem.posicao,
                    "profundidade": elem.profundidade,
                    "tag": elem.tag,
                    "classe": elem.classe,
                    "id": elem.elemento_id,
                    "link": elem.link,
                    "texto": elem.texto,
                    "pai": elem.pai,
                    "seletor_css": elem.seletor_css,
                    "xpath": elem.xpath,
                    "estavel": elem.estavel,
                }
            )

        tags = Counter()
        for elem in elementos_dict:
            tags[elem.get("tag", "desconhecido")] += 1

        return jsonify(
            {
                "sucesso": True,
                "id": mapa.id,
                "total": len(elementos_dict),
                "elementos": elementos_dict,
                "tags": dict(tags.most_common(10)),
                "data": mapa.data_mapeamento.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    except Exception as e:
        print(f"❌ Erro ao carregar mapa: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
    finally:
        session_db.close()


@app.route("/carregar_mapa_por_id", methods=["GET"])
@login_obrigatorio
def carregar_mapa_por_id():
    mapa_id = request.args.get("id")
    if not mapa_id:
        return jsonify({"erro": "ID não fornecido"}), 400

    session_db = SessionLocal()

    try:
        mapa = session_db.query(Mapa).filter(Mapa.id == mapa_id).first()

        if not mapa:
            return jsonify({"erro": "Mapa não encontrado"}), 404

        elementos_dict = []
        for elem in mapa.elementos:
            elementos_dict.append(
                {
                    "posicao": elem.posicao,
                    "profundidade": elem.profundidade,
                    "tag": elem.tag,
                    "classe": elem.classe,
                    "id": elem.elemento_id,
                    "link": elem.link,
                    "texto": elem.texto,
                    "pai": elem.pai,
                    "seletor_css": elem.seletor_css,
                    "xpath": elem.xpath,
                    "estavel": elem.estavel,
                }
            )

        return jsonify(
            {
                "sucesso": True,
                "id": mapa.id,
                "total": len(elementos_dict),
                "elementos": elementos_dict,
                "data": mapa.data_mapeamento.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    except Exception as e:
        print(f"❌ Erro ao carregar mapa por ID: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
    finally:
        session_db.close()


@app.route("/exportar", methods=["POST"])
@login_obrigatorio
def exportar():
    global cache_mapa
    if not cache_mapa["dados"]:
        return jsonify({"erro": "Nenhum mapa para exportar"}), 400
    formato = request.json.get("formato", "excel")
    dados = cache_mapa["dados"]
    if formato == "excel":
        df = pd.DataFrame(dados)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Estrutura")
        output.seek(0)
        return send_file(
            output,
            download_name=f'mapa_{cache_mapa["url"].replace("https://", "").replace("/", "_")}.xlsx',
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    elif formato == "json":
        output = io.BytesIO()
        output.write(json.dumps(dados, indent=2, ensure_ascii=False).encode("utf-8"))
        output.seek(0)
        return send_file(
            output,
            download_name=f'mapa_{cache_mapa["url"].replace("https://", "").replace("/", "_")}.json',
            as_attachment=True,
            mimetype="application/json",
        )
    elif formato == "csv":
        df = pd.DataFrame(dados)
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding="utf-8")
        output.seek(0)
        return send_file(
            output,
            download_name=f'mapa_{cache_mapa["url"].replace("https://", "").replace("/", "_")}.csv',
            as_attachment=True,
            mimetype="text/csv",
        )
    return jsonify({"erro": "Formato não suportado"}), 400


@app.route("/gerar_codigo", methods=["POST"])
@login_obrigatorio
def gerar():
    dados = request.json
    seletor = dados.get("seletor")
    tipo = dados.get("tipo", "css")
    ferramenta = dados.get("ferramenta", "playwright")
    codigo = gerar_codigo(seletor, tipo, ferramenta)
    return jsonify({"codigo": codigo})


def abrir_navegador():
    time.sleep(1.5)
    url = "http://127.0.0.1:5000"

    try:
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ]

        chrome_found = False
        for path in chrome_paths:
            if os.path.exists(path):
                subprocess.Popen([path, "--new-window", url], shell=False)
                chrome_found = True
                print("✅ Chrome aberto com sucesso!")
                break

        if not chrome_found:
            subprocess.Popen(["start", url], shell=True)
            print("✅ Navegador padrão aberto com sucesso!")

    except Exception as e:
        try:
            webbrowser.open(url, new=2)
            print("✅ Tentando com webbrowser...")
        except:
            print(f"❌ Erro ao abrir navegador: {e}")
            print(f"📋 Abra manualmente: {url}")


if __name__ == "__main__":
    print("🚀 Struct Analyzer Pro")
    print("🌐 Abrindo navegador...")
    threading.Thread(target=abrir_navegador, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
