import unicodedata
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from django.shortcuts import get_object_or_404, render, redirect
from InputHistory.models import InputOrder
from OutputHistory.models import OutputOrder
from Workers.models import Worker
from .models import Product, OutputOrderItem


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


def ModifyOutputOrders(request, orderid):
    order = get_object_or_404(OutputOrder, id=orderid)
    workers = Worker.objects.all()
    products = order.GetItems()
    all_products = Product.objects.all()

    if request.method == "POST":
        form_data = request.POST  # Use a different variable name

        # Update order details
        order.worker = Worker.objects.get(name=form_data.get("nameWorker"))
        order.date_created = form_data.get("dateCreation")
        order.save()

        # Update product quantities
        for product_item in products:
            product_item.quantity = form_data.get(f"quantityProduct_{product_item.product.id}")
            product_item.save()

            # Update product quantities and handle product deletions
        for product_item in products:
            quantity_key = f"quantityProduct_{product_item.product.id}"
            product_item.quantity = form_data.get(quantity_key)
            product_item.save()

            # Handle product deletions
            if int(form_data.get(quantity_key, 0)) == 0:
                product_item.delete()

        new_product_names = request.POST.getlist('newProductName[]')
        new_product_quantities = request.POST.getlist('newProductQuantity[]')

        for name, quantity in zip(new_product_names, new_product_quantities):
            if name:
                # Check if the product with the given name exists
                existing_product = Product.objects.filter(name=name).first()

                if existing_product:
                    # Add the existing product to the order
                    OutputOrderItem.objects.create(product=existing_product, quantity=quantity, outputOrder=order)

        return redirect('outputDetails', orderid)

    context = {
        "order": order,
        "id": orderid,
        "products": products,
        "workers": workers,  # Pass the worker names to the template to create datalist
        "all_products": all_products,  # Pass the product names to the template to create datalist
    }
    return render(request, "outputHistory-edit.html", context)
