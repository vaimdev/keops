from django.template.loader import BaseLoader
from django.template.loaders.app_directories import app_template_dirs
from django.template import TemplateDoesNotExist
from django.core import urlresolvers
from django.conf import settings
import jinja2

class Template(jinja2.Template):
    def render(self, context):
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        return super(Template, self).render(context_dict)

class Loader(BaseLoader):
    def load_template(self, template_name, template_dirs=None):
        try:
            template = self.env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise TemplateDoesNotExist(template_name)
        return template, template.filename
