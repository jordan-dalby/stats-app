from .resource_gatherers import ResourceGatherersHandler
from .resource_gatherers_custom import ResourceGatherersCustomHandler
from .build_tools import BuildToolsHandler

def get_handler(handler_name):
    handlers = {
        'resource-gatherers': ResourceGatherersHandler,
        'resource-gatherers-custom': ResourceGatherersCustomHandler,
        'build-tools': BuildToolsHandler
    }
    return handlers.get(handler_name)