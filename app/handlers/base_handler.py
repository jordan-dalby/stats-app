from abc import ABC, abstractmethod

class BaseHandler(ABC):
    @abstractmethod
    def add_stats(self, data):
        pass

    @abstractmethod
    def get_stats(self):
        pass

    @abstractmethod
    def update_highscores(self, stats):
        pass

    @abstractmethod
    def get_formatted_stats(self):
        pass

    @abstractmethod
    def get_friendly_name(self):
        pass