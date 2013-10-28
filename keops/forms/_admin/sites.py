from django.db import models
from django.contrib.admin import AdminSite
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
        from keops.db import get_db
        using = get_db(request)
        model = self.get_model(request.GET['model'])
        admin = model._admin
        action = request.GET['action']
        pk = request.GET.get('pk')
        if action in self._global_actions:
            action = self._global_actions[action]
        else:
            action = admin.get_actions(request)[action]
        queryset = None
        if pk:
            queryset = model.objects.using(using).filter(pk=pk)
        return action(admin, request, queryset)

    def get_model(self, model):
        # TODO Check model permission
        # TODO CACHE PERMISSION
        return models.get_model(*model.split('.'))

site = AdminSite()
