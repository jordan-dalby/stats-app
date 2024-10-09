from app.database import db
from .base_handler import BaseHandler
from sqlalchemy import func

class BuildToolsStats(db.Model):
    server_uid = db.Column(db.String(100), primary_key=True)
    server_type = db.Column(db.String(50), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    players = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class BuildToolsHighscores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_count = db.Column(db.Integer, nullable=False)
    players = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class BuildToolsHandler(BaseHandler):
    def add_stats(self, data):
        stats = BuildToolsStats(
            server_uid=data['server_uid'],
            server_type=data['server_type'],
            version=data['version'],
            players=data['players'],
            timestamp=func.now()
        )
        db.session.merge(stats)
        db.session.commit()
        return True

    def get_stats(self):
        one_hour_ago = func.datetime('now', '-1 hour')
        
        total_entries = db.session.query(func.count(BuildToolsStats.server_uid)).filter(
            BuildToolsStats.timestamp >= one_hour_ago
        ).scalar()

        total_players = db.session.query(func.sum(BuildToolsStats.players)).filter(
            BuildToolsStats.timestamp >= one_hour_ago
        ).scalar()

        server_type_stats = db.session.query(
            BuildToolsStats.server_type,
            func.count(BuildToolsStats.server_uid)
        ).filter(
            BuildToolsStats.timestamp >= one_hour_ago
        ).group_by(BuildToolsStats.server_type).all()

        version_distribution = db.session.query(
            BuildToolsStats.version,
            func.count(BuildToolsStats.server_uid)
        ).filter(
            BuildToolsStats.timestamp >= one_hour_ago
        ).group_by(BuildToolsStats.version).all()

        # Fetch the latest highscores
        latest_highscore = db.session.query(BuildToolsHighscores).order_by(
            BuildToolsHighscores.timestamp.desc()
        ).first()

        return {
            'summary': {
                'total_entries': total_entries or 0,
                'total_players': total_players or 0,
                'highscore_server_count': latest_highscore.server_count if latest_highscore else 0,
                'highscore_players': latest_highscore.players if latest_highscore else 0
            },
            'charts': [
                {
                    'title': 'Server Type Distribution',
                    'labels': [stat[0] for stat in server_type_stats],
                    'sizes': [stat[1] for stat in server_type_stats],
                    'chart_type': 'horizontal_bar'
                },
                {
                    'title': 'Version Distribution',
                    'labels': [stat[0] for stat in version_distribution],
                    'sizes': [stat[1] for stat in version_distribution],
                    'chart_type': 'horizontal_bar'
                }
            ]
        }

    def update_highscores(self):
        current_stats = self.get_stats()['summary']
        
        # Query the current highscores
        highscores = db.session.query(BuildToolsHighscores).order_by(
            BuildToolsHighscores.server_count.desc(),
            BuildToolsHighscores.players.desc()
        ).first()

        # Initialize new highscore values
        new_highscore = {
            'server_count': max(highscores.server_count if highscores else 0, current_stats['total_entries']),
            'players': max(highscores.players if highscores else 0, current_stats['total_players'])
        }

        # Check if any highscore was beaten
        if (not highscores or 
            new_highscore['server_count'] > highscores.server_count or
            new_highscore['players'] > highscores.players):
            
            # Create and add new highscore entry
            new_entry = BuildToolsHighscores(
                server_count=new_highscore['server_count'],
                players=new_highscore['players']
            )
            db.session.add(new_entry)
            db.session.commit()
            print("New highscore recorded!")
        else:
            print("No new highscore.")

    def get_formatted_stats(self):
        stats = self.get_stats()
        summary = stats['summary']

        formatted_stats = {
            'summary': [
                f'### Hourly Statistics',
                f"**Unique Servers:** {summary['total_entries']}",
                f"**Number of Players:** {summary['total_players']}",
                f'### All-Time Highscores',
                f"**Players:** {summary['highscore_players']}",
                f"**Servers:** {summary['highscore_server_count']}",
            ],
            'charts': stats['charts']
        }
        return formatted_stats

    def get_friendly_name(self):
        return "Build Tools"