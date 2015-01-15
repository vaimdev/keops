import os
from django.core.serializers.python import Serializer as PythonSerializer
from django.core import serializers


class Serializer(PythonSerializer):
    internal_use_only = False


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of Django template data.
    """
    from django.template import Context, Template
    name = stream_or_string.name
    filepath = os.path.splitext(name)[0]
    # adjust filepath
    options['filepath'] = filepath
    stream_or_string = Template(stream_or_string.read()).render(Context({}))
    return serializers.deserialize(filepath.split('.')[-1], stream_or_string, **options)
