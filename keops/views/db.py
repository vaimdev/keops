from django.shortcuts import render
from django.http import JsonResponse


def get_model(model):
    pass


def grid(request, db=None):
    return JsonResponse({})


def read(request, db=None):
    model = request.GET['model']
    return render(request, 'test.html')
    #return JsonResponse({'dbarg': db, 'request': str(request.db), 'model': model})
