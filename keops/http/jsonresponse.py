import json
from django.http import HttpResponse
from django.contrib import messages


def HttpJsonResponse(content, content_type='application/json', *args, **kwargs):
    return HttpResponse(json.dumps(content), content_type, *args, **kwargs)


# json decorator
def json_response(func):
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        try:
            data = json.dumps(objects)
            if 'callback' in request.REQUEST:
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                return HttpResponse(data, "text/javascript")
        except:
            data = json.dumps(str(objects))
        return HttpResponse(data, "application/json")
    return decorator


def HttpMessagesResponse(msgs):
    return HttpJsonResponse([{'success': m.level in [messages.INFO, messages.SUCCESS, messages.WARNING],
                              'alert': m.tags, 'message': m.message} for m in msgs])
