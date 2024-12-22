from flask import Flask
import logging, os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__, instance_path="/instance")

    from app.views import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app 