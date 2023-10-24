from django.shortcuts import render
from .models import Worker, OutputOrder

# Create your views here.


def history(request):
    worker = Worker.objects.get(name="Juan")
    orders = OutputOrder.objects.filter(worker=worker)
    context = {
        'orders': orders
    }

    return render(request, 'outputHistoryWorker.html', context)


def outputHistory(request):
    worker = Worker.objects.get(name="Juan")
    orders = OutputOrder.objects.filter(worker=worker)
    context = {
        'orders': orders
    }

    return render(request, 'outputHistory.html', context)


def inputHistory(request):
    return render(request, 'inputHistory.html')
