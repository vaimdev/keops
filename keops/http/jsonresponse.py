import json
from django.http import JsonResponse
from django.contrib import messages


def HttpMessagesResponse(msgs):
    return JsonResponse([{'success': m.level in [messages.INFO, messages.SUCCESS, messages.WARNING],
                              'alert': m.tags, 'message': m.message} for m in msgs])
