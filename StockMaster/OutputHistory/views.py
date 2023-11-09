import unicodedata
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
<<<<<<< HEAD
from django.shortcuts import get_object_or_404, render

=======
from django.shortcuts import render
>>>>>>> 3eba94c75b21fd678e5be6c1f5388b670a92f0f7
from InputHistory.models import InputOrder
from OutputHistory.models import OutputOrder
from Workers.models import Worker


@login_required(login_url='login')
def OutputHistory(request):
    """
    Displays the output history page with search and date range filtering.

    Returns:
        A rendered output history page with search and date range filtering.
    """
    searchQuery = request.GET.get("search")
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    outputOrders = OutputOrder.objects.all()

    if searchQuery:
        search_query_normalized = RemoveAccents(searchQuery).lower()
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
def InputHistory(request):
    """
    Displays the input history page with search and date range filtering.

    Returns:
        A rendered input history page with search and date range filtering.
    """
    searchQuery = request.GET.get("search")
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    inputOrders = InputOrder.objects.all()

    if searchQuery:
        search_query_normalized = RemoveAccents(searchQuery).lower()
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


def RemoveAccents(input_str):
    """
    Removes accents from a string.

    Args:
        input_str (str): The string from which to remove accents.

    Returns:
        str: The string without accents.
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def outputDetails(request, orderid):
    output_order = get_object_or_404(OutputOrder, id=orderid)
    worker_name = output_order.worker.name

    total_price = output_order.GetTotal()
    total_quantity = output_order.GetQuantity()
    date = output_order.date_created

    products = {}

    for product in output_order.outputorderitem_set.all():
        products[product] = product.quantity * product.product.price

    context = {
        'output_order': output_order,
        'worker_name': worker_name,
        'total_price': total_price,
        'total_quantity': total_quantity,
        'date': date,
        'products': products
    }

    return render(request, 'outputHistoryWorker.html', context)


def redirection(request):
    context = {

    }
    return render(request, 'inventory.html', context)
