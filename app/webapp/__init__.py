from flask import Flask
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap

from app.webapp.config import Config
from app.chat import bots

socketio = SocketIO()
bootstrap = Bootstrap()


def create_app(debug=True, config_class=Config):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config.from_object(config_class)
    bootstrap.init_app(app)
    bots.init_bots()
    from .main import bp
    app.register_blueprint(bp)
    socketio.init_app(app)
    return app

