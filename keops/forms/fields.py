from django import forms
from .widgets import *

__all__ = ['GridField']

class GridField(forms.Field):
    widget = GridWidget
    input_direct = False

    def __init__(self, queryset, required=False, label=None, help_text=None, *args, **kwargs):
        self.queryset = queryset
        super(GridField, self).__init__(required=required, label=label, help_text=help_text, *args, **kwargs)

class BetweenDateField(forms.CharField):
    widget = BetweenDateWidget
