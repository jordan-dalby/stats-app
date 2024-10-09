import os

# Flask settings
DEBUG = os.getenv('DEBUG', 'False') == 'True'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 46423))

# Authentication
# Each request will require their auth token to match, otherwise no data will be added
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
if AUTH_TOKEN is None:
    raise ValueError("AUTH_TOKEN environment variable is not set")

# Database
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Discord Webhook
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
if WEBHOOK_URL is None:
    raise ValueError("WEBHOOK_URL environment variable is not set")

# Stats collection interval (in seconds)
STATS_INTERVAL = int(os.getenv('STATS_INTERVAL', 3600)) # 3600 = 1 hour

# Handlers
ENABLED_HANDLERS = [
    
    # Released
    'resource-gatherers',
    
    # Unreleased
    #'resource-gatherers-custom',
    #'build-tools',

]