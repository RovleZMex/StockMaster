import unicodedata
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from InputHistory.models import InputOrder
from OutputHistory.models import OutputOrder


# TODO CREATE A VIEW FOR ALL ORDERS (OUTPUT/INPUT)
@login_required(login_url='login')
def outputHistory(request):
    searchQuery = request.GET.get("search")
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    outputOrders = OutputOrder.objects.all()

    if searchQuery:
        search_query_normalized = remove_accents(searchQuery).lower()
        outputOrders = outputOrders.filter(
            Q(worker__name__icontains=search_query_normalized)
        )

    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
        outputOrders = outputOrders.filter(date_created__range=[start_date_obj, end_date_obj])

    paginator = Paginator(outputOrders, 5)
    pageNumber = request.GET.get("page")
    page_obj = paginator.get_page(pageNumber)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'outputHistory.html', context)


@login_required(login_url='login')
def inputHistory(request):
    searchQuery = request.GET.get("search")
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    inputOrders = InputOrder.objects.all()

    if searchQuery:
        search_query_normalized = remove_accents(searchQuery).lower()
        inputOrders = inputOrders.filter(
            Q(id__icontains=search_query_normalized)
        )

    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
        inputOrders = inputOrders.filter(date_created__range=[start_date_obj, end_date_obj])

    paginator = Paginator(inputOrders, 5)
    pageNumber = request.GET.get("page")
    page_obj = paginator.get_page(pageNumber)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'inputHistory.html', context)


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
