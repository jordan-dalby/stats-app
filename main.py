from flask import Flask
from flask_cors import CORS
from app.api import api_bp
from app.database import db
from app.stats_manager import StatsManager
import config

app = Flask(__name__)

def create_app():
    app.config.from_object(config)

    CORS(app)

    # Initialize extensions
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(api_bp)

    # Initialize StatsManager
    stats_manager = StatsManager(app)
    stats_manager.start()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)