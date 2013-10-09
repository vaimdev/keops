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
    filepath = os.path.splitext(options.get('filepath'))[0]
    # adjust filepath
    options['filepath'] = filepath
    stream_or_string = Template(stream_or_string.read()).render(Context({}))
    serializers.deserialize(os.path.splitext(filepath)[1], stream_or_string, **options)
