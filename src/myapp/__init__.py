import os

from flask import Flask

from myapp.config import INSTANCE_DIR, Config
from myapp.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__, instance_path=str(INSTANCE_DIR))
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from myapp.api.health import health_bp
    from myapp.api.questions import api_questions_bp, register_api_error_handlers
    from myapp.web.auth import auth_bp
    from myapp.web.questions import questions_bp
    from myapp.web.users import users_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(api_questions_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(users_bp)
    register_api_error_handlers(app)

    from myapp.commands import register_commands

    register_commands(app)

    return app
