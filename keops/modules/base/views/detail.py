from django.shortcuts import render
from django.utils.text import capfirst
from keops.db import get_db
from keops.views.db import get_model

def index(request):
    using = get_db(request)
    view_type = request.GET.get('type', 'dialog')
    model = get_model(request.GET)
    field = request.GET.get('field')
    pk = request.GET.get('pk')
    if field:
        field = getattr(model, field)
        related = field.related
        rel_model = related.model
        content = rel_model._admin.render_form()
        return render(request, 'keops/forms/detail_dialog.html', {
            'header': capfirst(field.verbose_name or field.name),
            'content': content
        })
