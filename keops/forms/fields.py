from django.forms import Field
from . import widgets

class GridField(Field):
    widget = widgets.GridWidget
    input_direct = False

    def __init__(self, queryset, required=False, label=None, help_text=None, *args, **kwargs):
        self.queryset = queryset
        super(GridField, self).__init__(required=required, label=label, help_text=help_text, *args, **kwargs)

class OneToManyField(GridField):
    pass
