
from django.template.loaders import app_directories

class Loader(app_directories.Loader):
    is_usable = True
    _lookup = {}

    def load_template(self, template_name, template_dirs=None):
        if template_name.endswith('.mako'):
            source, origin = self.load_template_source(template_name, template_dirs)
            template = Template(source, lookup=self._get_lookup('mako'))
        else:
            template, origin = super(Loader, self).load_template(template_name, template_dirs)
        return template, origin
    
    def _get_lookup(self, template_lang):
        if not template_lang in Loader._lookup:
            if template_lang == 'mako':
                from mako.lookup import TemplateLookup
                Loader._lookup['mako'] = TemplateLookup(directories=app_directories.app_template_dirs[::-1], input_encoding='utf-8')
        return Loader._lookup[template_lang]
