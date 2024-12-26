import logging
from flask import Flask
from flask_limiter import Limiter

from app.functions.utils import get_client_ip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(
    get_client_ip, 
    default_limits=["100 per day", "10 per minute"],
    storage_uri="memory://"
)

def create_app():
    app = Flask(__name__, instance_path="/instance")

    limiter.init_app(app)

    from app.views import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app
