from app.database import db
from .base_handler import BaseHandler
from sqlalchemy import func

class ResourceGatherersCustomStats(db.Model):
    server_uid = db.Column(db.String(100), primary_key=True)
    gatherers = db.Column(db.Integer, nullable=False)
    server_type = db.Column(db.String(50), nullable=False)
    version = db.Column(db.String(50), nullable=False)
    players = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class ResourceGatherersCustomHighscores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_count = db.Column(db.Integer, nullable=False)
    total_gatherers = db.Column(db.Integer, nullable=False)
    gatherers = db.Column(db.Integer, nullable=False)
    players = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

class ResourceGatherersCustomHandler(BaseHandler):
    def add_stats(self, data):
        stats = ResourceGatherersCustomStats(
            server_uid=data['server_uid'],
            gatherers=data['gatherers'],
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
        
        total_entries = db.session.query(func.count(ResourceGatherersCustomStats.server_uid)).filter(
            ResourceGatherersCustomStats.timestamp >= one_hour_ago
        ).scalar()

        total_gatherers = db.session.query(func.sum(ResourceGatherersCustomStats.gatherers)).filter(
            ResourceGatherersCustomStats.timestamp >= one_hour_ago
        ).scalar()

        total_players = db.session.query(func.sum(ResourceGatherersCustomStats.players)).filter(
            ResourceGatherersCustomStats.timestamp >= one_hour_ago
        ).scalar()

        server_type_stats = db.session.query(
            ResourceGatherersCustomStats.server_type,
            func.count(ResourceGatherersCustomStats.server_uid)
        ).filter(
            ResourceGatherersCustomStats.timestamp >= one_hour_ago
        ).group_by(ResourceGatherersCustomStats.server_type).all()

        version_distribution = db.session.query(
            ResourceGatherersCustomStats.version,
            func.count(ResourceGatherersCustomStats.server_uid)
        ).filter(
            ResourceGatherersCustomStats.timestamp >= one_hour_ago
        ).group_by(ResourceGatherersCustomStats.version).all()

        highest_gatherer_count = db.session.query(func.max(ResourceGatherersCustomStats.gatherers)).filter(
            ResourceGatherersCustomStats.timestamp >= one_hour_ago
        ).scalar()

        # Fetch the latest highscores
        latest_highscore = db.session.query(ResourceGatherersCustomHighscores).order_by(
            ResourceGatherersCustomHighscores.timestamp.desc()
        ).first()

        return {
            'summary': {
                'total_entries': total_entries or 0,
                'total_gatherers': total_gatherers or 0,
                'total_players': total_players or 0,
                'highest_gatherer_count': highest_gatherer_count or 0,
                'highscore_server_count': latest_highscore.server_count if latest_highscore else 0,
                'highscore_total_gatherers': latest_highscore.total_gatherers if latest_highscore else 0,
                'highscore_gatherers': latest_highscore.gatherers if latest_highscore else 0,
                'highscore_players': latest_highscore.players if latest_highscore else 0
            },
            'charts': [
                {
                    'title': 'Server Type Distribution',
                    'labels': [stat[0] for stat in server_type_stats],
                    'sizes': [stat[1] for stat in server_type_stats],
                    'chart_type': 'bar'
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
        highscores = db.session.query(ResourceGatherersCustomHighscores).order_by(
            ResourceGatherersCustomHighscores.server_count.desc(),
            ResourceGatherersCustomHighscores.total_gatherers.desc(),
            ResourceGatherersCustomHighscores.gatherers.desc(),
            ResourceGatherersCustomHighscores.players.desc()
        ).first()

        # Initialize new highscore values
        new_highscore = {
            'server_count': max(highscores.server_count if highscores else 0, current_stats['total_entries']),
            'total_gatherers': max(highscores.total_gatherers if highscores else 0, current_stats['total_gatherers']),
            'gatherers': max(highscores.gatherers if highscores else 0, current_stats['highest_gatherer_count']),
            'players': max(highscores.players if highscores else 0, current_stats['total_players'])
        }

        # Check if any highscore was beaten
        if (not highscores or 
            new_highscore['server_count'] > highscores.server_count or
            new_highscore['total_gatherers'] > highscores.total_gatherers or
            new_highscore['gatherers'] > highscores.gatherers or
            new_highscore['players'] > highscores.players):
            
            # Create and add new highscore entry
            new_entry = ResourceGatherersCustomHighscores(
                server_count=new_highscore['server_count'],
                total_gatherers=new_highscore['total_gatherers'],
                gatherers=new_highscore['gatherers'],
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
                f"**Total Gatherers:** {summary['total_gatherers']}",
                f"**Most Gatherers:** {summary['highest_gatherer_count']}",
                f'### All-Time Highscores',
                f"**Players:** {summary['highscore_players']}",
                f"**Servers:** {summary['highscore_server_count']}",
                f"**Gatherers:** {summary['highscore_gatherers']}",
                f"**Total Gatherers:** {summary['highscore_total_gatherers']}"
            ],
            'charts': stats['charts']
        }
        return formatted_stats

    def get_friendly_name(self):
        return "Resource Gatherers: Custom"