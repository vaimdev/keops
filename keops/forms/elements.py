
class Element(object):
    template_name = ''

    def __init__(self):
        self.node = None
        self.tag_name = ''
        self.attrs = {}
        self.children = []

    def __iter__(self):
        for child in self.children:
            yield child

    def __getitem__(self, item):
        return self.attrs.get(item)

    def __setitem__(self, key, value):
        self.attrs[key] = value

    def render(self, *args, **kwargs):
        pass

class Button(Element):
    pass

class Field(Element):
    """
    Render a field element.
    """
    pass

class Fieldset(Element):
    """
    Render a fieldset element.
    """
    pass

class Form(Element):
    pass

class Grid(Field):
    """
    Render grid element.
    """
    pass

class Container(Element):
    """
    Render a field container element.
    """
    pass

class Tabset(Element):
    pass

class Tab(Element):
    pass
