import threading
import time
import requests
import json
import base64
from app.handlers import get_handler
import config
from utils.chart_helper import create_charts

class StatsManager:
    _instance = None
    
    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super(StatsManager, cls).__new__(cls)
            cls._instance.app = app
            cls._instance.handlers = {name: get_handler(name)() for name in config.ENABLED_HANDLERS}
        return cls._instance

    def start(self):
        thread = threading.Thread(target=self._run_periodic_tasks)
        thread.daemon = True
        thread.start()

    def _run_periodic_tasks(self):
        while True:
            with self.app.app_context():
                for handler in self.handlers.values():
                    handler.update_highscores()
                self.collect_and_send_stats()
            time.sleep(config.STATS_INTERVAL)

    @classmethod
    def is_valid_handler(cls, handler_name):
        return handler_name in config.ENABLED_HANDLERS

    @classmethod
    def add_stats(cls, handler_name, data):
        handler = cls._instance.handlers[handler_name]
        return handler.add_stats(data)

    @classmethod
    def get_all_stats(cls):
        return {name: cls._instance.handlers[name].get_formatted_stats() for name in cls._instance.handlers}

    def collect_and_send_stats(self):
        all_stats = self.get_all_stats()
        for handler_name, stats in all_stats.items():
            handler = self.handlers[handler_name]
            
            # Create charts
            charts_data = stats.get('charts', [])
            if charts_data:
                chart_image = create_charts(charts_data)
            else:
                chart_image = None

            # Prepare the message
            message = f"## {handler.get_friendly_name()} Stats\n"
            for value in stats['summary']:
                message += f"{value}\n"

            # Send message to Discord
            self.send_discord_message(message, chart_image)

    def send_discord_message(self, content, image_data=None):
        payload = {
            "content": "",
            "embeds": [
                {
                    "description": content,
                    "image": {"url": "attachment://chart.png"}
                }
            ]
        }

        files = {}
        
        if image_data:
            # Remove the "data:image/png;base64," prefix
            image_data = image_data.split(',')[1]
            image_binary = base64.b64decode(image_data)
            files = {
                'file': ('chart.png', image_binary, 'image/png')
            }

        try:
            response = requests.post(
                config.WEBHOOK_URL,
                data={'payload_json': (None, json.dumps(payload), 'multipart/form-data')},
                files=files
            )
            response.raise_for_status()
            print(f"Message sent successfully")
        except requests.RequestException as e:
            print(f"Failed to send message to Discord: {e}")
            if response.text:
                print(f"Response content: {response.text}")