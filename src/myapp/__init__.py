from flask import Flask

from myapp.config import Config
from myapp.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from myapp.api.health import health_bp
    from myapp.web.auth import auth_bp
    from myapp.web.questions import questions_bp
    from myapp.web.users import users_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(questions_bp)
    app.register_blueprint(users_bp)

    from myapp.commands import register_commands

    register_commands(app)

    return app
