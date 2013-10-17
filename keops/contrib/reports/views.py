import os
import json
from collections import OrderedDict
from django.shortcuts import render
from django import forms
from django.conf import settings
from keops.db import models
from keops.db import get_connection
from keops.modules.base.models import Report

__all__ = ['ReportForm', 'form', 'find_report_file', 'get_form']

FORM_CACHE = {}

class ReportForm(forms.Form):
    _report_file = ''
    _params_file = ''
    _report_id = None
    _params = {}

def _get_initial_data(form):

    def eval_default(val):
        if isinstance(val, str):
            context = {'value': None}
            exec(val, globals(), context)
            return context['value']

    items = form._params['items']
    initial = {}
    for param in items:
        if 'default' in param:
            initial[param['name']] = str(eval_default(param['default']))
        elif 'value' in param:
            initial[param['name']] = param['value']
    return initial

def find_report_file(name):
    """
    Detect real report file name.
    """
    name = name.split('/')
    app_label = name[0]
    app = models.get_app(app_label)
    return os.path.join(os.path.dirname(app.__file__), *name[1:])

def get_field(param):
    field_type = param.get('field_type')
    attrs = {}
    for p in param:
        if not p in ['field_name', 'query', 'default', 'field_type', 'name', 'static', 'generate_sql', 'value']:
            attrs[p] = param[p]
        if p == 'query':
            conn = get_connection()
            c = conn.cursor()
            c.execute(param[p])
            attrs['choices'] = [[r[0], (len(r) == 1 and r[0]) or r[1]] for r in c.fetchall()]
    return getattr(forms, field_type, None)(**attrs)


def get_form(report, params):
    if params in FORM_CACHE:
        form = FORM_CACHE[params]

    elif os.path.isfile(params):
        data = json.load(open(params, 'r', encoding=settings.DEFAULT_CHARSET))

        items = data['items']
        form = { param['name']: get_field(param) for param in items }
        form = type('_ReportForm', (ReportForm,), form)
        form._report_file = report._report_file
        form._params_file = params
        form._params = data
        FORM_CACHE[params] = form

    return form(initial=_get_initial_data(form))

def form(request):
    """
    Render report form view.
    """
    report = Report.objects.get(pk=request.GET['id'])
    report._report_file = find_report_file(report.name)
    params = report._report_file.split('.')[0] + '.json'
    form = get_form(report, params)
    print(str(form))
    return render(request, 'keops/forms/filter_form.html', {
        'header': os.path.basename(params).split('.')[0],
        'form': form,
    })
