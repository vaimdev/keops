from django.forms.util import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms import widgets

class GridWidget(widgets.Widget):
    pass

class BetweenDateWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        self.widgets = [widgets.DateInput(), widgets.DateInput()]
        super(BetweenDateWidget, self).__init__(attrs)

    def decompress(self, value):
        return [None, None]
