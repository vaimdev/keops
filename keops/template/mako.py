from django.template.loader import render_to_string
from mako import template

__all__ = ['Template', 'render']

class Template(template.Template):
    def render(self, context):
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        return super(Template, self).render(**context_dict)

def render(filename, **kwargs):
    return render_to_string(filename, kwargs)
