from flask import Flask
from flask_bootstrap import Bootstrap
from pathlib import Path
from .config import DefaultConfig


def create_app():
    # TODO: improve configuration, create dev/test/prod envs
    project_root = Path().absolute()

    app = Flask(__name__, instance_relative_config=True, instance_path=project_root)
    app.config.from_object(DefaultConfig)
    app.config.from_pyfile('.env', silent=True)

    Bootstrap(app)

    with app.app_context():
        from . import views  # could use "blueprint" here

    return app
