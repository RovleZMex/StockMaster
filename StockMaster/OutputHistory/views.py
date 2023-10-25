from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from OutputHistory.models import OutputOrder
from InputHistory.models import InputOrder


# Create your views here.

@login_required(login_url='login')
def history(request):
    return render(request, 'outputHistoryWorker.html')


@login_required(login_url='login')
def outputHistory(request):
    outputOrders = OutputOrder.objects.all()
    context = {
        'orders': outputOrders,
    }
    return render(request, 'outputHistory.html', context)


@login_required(login_url='login')
def inputHistory(request):
    inputOrders = InputOrder.objects.all()
    context = {
        'orders': inputOrders
    }
    return render(request, 'inputHistory.html', context)


