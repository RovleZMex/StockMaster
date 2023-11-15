import unicodedata
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from django.http import JsonResponse

from django.shortcuts import get_object_or_404, render, redirect
from django.shortcuts import render
from InputHistory.models import InputOrder, InputOrderItem
from OutputHistory.models import OutputOrder
from Product.models import Product
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


@login_required(login_url='login')
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

    return render(request, 'outputHistory-details.html', context)


@login_required(login_url='login')
def inputOrderDetails(request, orderid):
    inputOrder = get_object_or_404(InputOrder, id=orderid)

    total = 0
    totalQuantity = 0
    for product in inputOrder.inputorderitem_set.all():
        total += product.getSubtotal()
        totalQuantity += product.quantity

    context = {
        'order': inputOrder,
        'totalPrice': round(total, 2),
        'totalQuantity': totalQuantity
    }
    return render(request, 'inputHistory-details.html', context)


@login_required(login_url='login')
def inputOrderEdit(request, orderid):
    if request.method == 'POST':
        order = InputOrder.objects.get(id=orderid)
        if request.POST.get("date") != '':
            date = request.POST["date"] + "-00:00:00"
            order.date_created = datetime.strptime(date,'%Y-%m-%d-%H:%M:%S')
            order.save()
        # Delete current items in the order
        for item in order.inputorderitem_set.all():
            item.product.quantity -= item.quantity
            item.product.save()
            item.delete()

        for i in range(1, len(request.POST) // 2):  # 2 attributes per item
            try:
                productName = request.POST[f"product{i}"]
                quantity = request.POST[f"quantity{i}"]
                product = Product.objects.get(name__icontains=productName)
                product.quantity += int(quantity)
                product.save()
                # create the new items for the list
                InputOrderItem.objects.create(
                    product=product,
                    quantity=quantity,
                    inputOrder=order
                )
            except:
                pass
        return redirect('inputHistory')

    order = get_object_or_404(InputOrder, id=orderid)
    allProducts = Product.objects.all()

    context = {
        'order': order,
        'allProducts': allProducts,
    }

    return render(request, 'inputHistory-edit.html', context)


@login_required(login_url="login")
def deleteOrder(request):
    if request.method == "POST":
        id = int(request.POST["orderid"])
        order = InputOrder.objects.get(id=id)
        for item in order.inputorderitem_set.all():
            item.product.quantity -= item.quantity
            item.product.save()
        order.delete()
        return JsonResponse({
            'success': True,
        })
    return JsonResponse({
        'success': False,
    })
