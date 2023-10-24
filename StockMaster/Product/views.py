from django.shortcuts import render

# Create your views here.


def history(request):
    return render(request, 'outputHistoryWorker.html')


def outputHistory(request):
    return render(request, 'outputHistory.html')


def inputHistory(request):
    return render(request, 'inputHistory.html')
