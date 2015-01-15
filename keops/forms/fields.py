from django import forms
from .widgets import *


class ModelChoiceField(forms.ModelChoiceField):
    pass


class GridField(forms.Field):
    widget = GridWidget
    input_direct = False

    def __init__(self, queryset, required=False, label=None, help_text=None, *args, **kwargs):
        self.queryset = queryset
        super(GridField, self).__init__(required=required, label=label, help_text=help_text, *args, **kwargs)


class DateIntervalField(forms.CharField):
    widget = DateIntervalWidget
