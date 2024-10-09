# Stats Server

## Overview

Stats Server is a Flask-based application designed to collect, process, and visualize statistical data from various sources. It uses a modular handler system to manage different types of statistics and provides Discord integration for easy reporting.

## Features

- Modular handler system for different types of statistics
- Automatic data collection and processing
- Generation of various chart types (pie, bar, horizontal bar)
- Discord integration for reporting statistics
- Highscore tracking for each handler
- RESTful API for data submission

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jordan-dalby/mod-stats.git
   cd mod-stats
   ```

2. Create a virtual environment and activate it

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your configuration:
   - Set the required environment variables, or
   - Edit `config.py` and set your Discord webhook URL and other configuration options

## Usage

1. Start the Flask server:
   ```
   python main.py
   ```
   This can also be done with waitress if properly set up

2. The server will start and begin collecting stats at the interval specified in your config file.

3. To submit data to a handler, send a POST request to `/submit` with the following format:
   ```json
   {
     "handler": "handler_name",
     "data_field_1": value1,
     "data_field_2": value2
   }
   ```

4. Stats will be automatically collected and sent to the specified Discord channel at regular, configurable intervals.

## Adding New Handlers

1. Create a new file in the `app/handlers/` directory (e.g., `new_handler.py`).
2. Implement a new handler class that inherits from `BaseHandler`.
3. Add the new handler to the `ENABLED_HANDLERS` list in `config.py`.

Example of a new handler:

```python
from app.database import db
from .base_handler import BaseHandler

class MyHandlerStats(db.Model):
    # Your table template
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class MyHandlerHighscores(db.Model):
    # Your table template
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class NewHandler(BaseHandler):
    def add_stats(self, data):
        # Implementation for adding stats
        pass

    def get_stats(self):
        # Implementation for retrieving stats
        pass

    def update_highscores(self, stats):
        # Implementation for updating highscores
        pass

    def get_formatted_stats(self):
        # Implementation for getting formatted stats
        pass

    def get_friendly_name(self):
        return "New Handler Name"
```

Check out the existing handlers for more help.

## Configuration

Key configuration options in `config.py`:

- `WEBHOOK_URL`: Discord webhook URL for sending stats
- `STATS_INTERVAL`: Interval (in seconds) for collecting and sending stats
- `ENABLED_HANDLERS`: List of enabled handler names
- `SQLALCHEMY_DATABASE_URI`: Database connection string

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.