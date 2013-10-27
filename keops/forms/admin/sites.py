from django.db import models
from collections import OrderedDict
from .actions import delete_selected, duplicate_selected


class AdminSite(object):
    def __init__(self):
        self._global_actions = OrderedDict()
        self._global_actions['delete_selected'] = delete_selected
        self._global_actions['duplicate_selected'] = duplicate_selected

    def add_action(self, action, name=None):
        """
        Register an action to be available globally.
        """
        name = name or action.__name__
        self._global_actions[name] = action

    def disable_action(self, name):
        """
        Disable a globally-registered action. Raises KeyError for invalid names.
        """
        del self._global_actions[name]

    def get_action(self, name):
        """
        Explicitly get a registered global action whether it's enabled or
        not. Raises KeyError for invalid names.
        """
        return self._global_actions[name]

    @property
    def actions(self):
        """
        Get all the enabled actions as an iterable of (name, func).
        """
        return self._global_actions.items()

    def dispatch_action(self, request):
        model = request.GET['model']

    def get_model(self, model):
        return models.get_model(*model.split('.'))

site = AdminSite()
