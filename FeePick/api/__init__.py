from .benifit import _benefit_api
from .user import _user_api


def add_namespaces(api):

    api.add_namespace(_benefit_api)
    api.add_namespace(_user_api)
