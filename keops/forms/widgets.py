from django.forms.util import flatatt
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django import forms
from django.forms import widgets

class GridWidget(widgets.Widget):
    pass

class DateIntervalWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        super(DateIntervalWidget, self).__init__([forms.DateField.widget(), forms.DateField.widget()], attrs)

    def decompress(self, value):
        return [None, None]
