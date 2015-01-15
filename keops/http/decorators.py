from django.http import JsonResponse


# json decorator
def json_response(func):
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        return JsonResponse(objects)
    return decorator
