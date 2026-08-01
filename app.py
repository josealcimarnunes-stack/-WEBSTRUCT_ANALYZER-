from flask import Flask
import config
from database.connection import init_db


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializa o Banco de Dados
    init_db(app)

    # Registro dos Blueprints de Rotas
    from routes.auth_routes import auth_bp
    from routes.scraping_routes import scraping_bp
    from routes.map_routes import map_bp
    from routes.export_routes import export_bp
    from routes.selectors_routes import selectors_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(scraping_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(selectors_bp)

    return app
