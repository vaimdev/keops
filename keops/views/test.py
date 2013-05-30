
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'orun/app.html', {'site_name': 'PREFEITURA MUNICIPAL DE MODELO'})
