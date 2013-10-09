import os
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer


class Serializer(PythonSerializer):
    """
    Convert a queryset to TXT.
    """
    internal_use_only = False

    pass


def Deserializer(stream_or_string, **options):
    """
    Deserialize a stream or string of TXT data.
    """
    def import_file(cls, filename):
        try:
            i = 0
            cols = []
            row = 0
            objects = []
            for line in stream_or_string.splitlines():
                pk = None
                row += 1
                line = line.replace(chr(9), ';').split(';')
                if i == 0:
                    cols = line
                    i += 1
                else:
                    data = line
                    kwargs = {}
                    cell = 0
                    for col in cols:
                        if cell > len(data):
                            break
                        kwargs[col] = data[cell].strip()
                        cell += 1
                    if len(kwargs) > 0:
                        pk = kwargs.pop('pk', None)
                        obj = {'model': cls, 'fields': kwargs}
                        if pk:
                            obj['pk'] = pk
                        objects.append(obj)
            if objects:
                return PythonDeserializer(objects, **options)
        except Exception as e:
            print('Error importing file: "%s", line: %i' % (filename, row), e)
            raise

    filepath = options.pop('filepath')
    if filepath:
        path = filepath.split(os.path.sep)
        model = '%s.%s' % (path[-3], os.path.splitext(path[-1])[0])
        return import_file(model, filepath)