import logging, yaml, os
from flask import Flask
from flask_limiter import Limiter

from app.functions.utils import get_client_ip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(
    get_client_ip, 
    default_limits=["10 per minute"],
    storage_uri="memory://"
)

def create_app():
    app = Flask(__name__, instance_path="/instance")

    limiter.init_app(app)
    
    config_files = ['config.yaml', 'site.yaml', 'devices.yaml', 'commands.yaml']

    for config_file in config_files:
        config_path = os.path.join("/instance", config_file)

        # Create empty config files if they don't exist
        if not os.path.exists(config_path):
            with open(config_path, "w") as f:
                pass
        
        # Load the config files into the app config
        with open(config_path, 'r') as file:
            config_yaml =  yaml.safe_load(file) or {}
        app.config[config_file.split('.')[0].upper()] = config_yaml
    

    from app.views import main
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app
