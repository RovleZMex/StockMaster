import unicodedata
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from InputHistory.models import InputOrder, InputOrderItem
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
            Q(worker__name__icontains=search_query_normalized) |
            Q(id__icontains=search_query_normalized)
        )

    if start_date and end_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
        outputOrders = outputOrders.filter(date_created__range=[start_date_obj, end_date_obj])

    paginator = Paginator(outputOrders.order_by("-date_created"), 10)
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
    order_type = request.GET.get('order_type')
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

    if order_type and order_type != "all":
        inputOrders = inputOrders.filter(isExternal=True if order_type == "external" else False)

    paginator = Paginator(inputOrders.order_by("-date_created"), 10)
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


@login_required(login_url="login")
def ModifyOutputOrders(request, orderid):
    order = get_object_or_404(OutputOrder, id=orderid)
    workers = Worker.objects.all()
    all_products = Product.objects.all()

    if request.method == "POST":
        form_data = request.POST

        # Update order details
        order.worker = Worker.objects.get(name=form_data.get("nameWorker"))
        order.date_created = form_data.get("dateCreation")
        order.save()

        # Update existing product quantities and handle deletions
        for product_item in order.GetItems():
            quantity_key = f"quantityProduct_{product_item.product.id}"
            new_quantity = int(form_data.get(quantity_key, 0))
            old_quantity = product_item.quantity

            # Subtract from available product quantity
            product_item.product.quantity -= (new_quantity - old_quantity)
            product_item.product.save()  # This line updates the product quantity

            product_item.quantity = new_quantity
            product_item.save()

            # Handle product deletions
            if new_quantity == 0:
                product_item.delete()

        # Add new products to the order
        new_product_names = form_data.getlist('newProductName[]')
        new_product_quantities = form_data.getlist('newProductQuantity[]')

        for name, quantity in zip(new_product_names, new_product_quantities):
            if name:
                existing_product = Product.objects.filter(name=name).first()

                if existing_product:
                    # Update existing product quantity
                    existing_item = OutputOrderItem.objects.filter(
                        product=existing_product, outputOrder=order
                    ).first()
                    if existing_item:
                        existing_item.quantity += int(quantity)
                        existing_item.save()
                        existing_product.quantity -= int(quantity)
                        existing_product.save()  # Update existing product quantity in the inventory
                    else:
                        OutputOrderItem.objects.create(
                            product=existing_product, quantity=quantity, outputOrder=order
                        )
                        existing_product.quantity -= int(quantity)
                        existing_product.save()  # Update existing product quantity in the inventory
                else:
                    # Add new product to the order
                    new_product = Product.objects.create(name=name)
                    OutputOrderItem.objects.create(
                        product=new_product, quantity=quantity, outputOrder=order
                    )
                    new_product.quantity -= int(quantity)
                    new_product.save()  # Update new product quantity in the inventory

        return redirect('outputDetails', orderid)

    # Max quantity calculation
    max_quantities = []
    for product_item in order.GetItems():
        max_quantity = product_item.product.quantity + product_item.quantity
        max_quantities.append(max_quantity)

    context = {
        "order": order,
        "id": orderid,
        "workers": workers,
        "products": zip(order.GetItems(), max_quantities),  # Make sure to retrieve existing products
        "all_products": all_products,
    }
    return render(request, "outputHistory-edit.html", context)


@login_required(login_url="login")
def deleteOrderOutput(request):
    if request.method == "POST":
        id = int(request.POST["orderid"])
        order = OutputOrder.objects.get(id=id)
        for item in order.outputorderitem_set.all():
            item.product.quantity += item.quantity
            item.product.save()
        order.delete()
        return JsonResponse({
            'success': True,
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url='login')
def inputOrderDetails(request, orderid):
    inputOrder = get_object_or_404(InputOrder, id=orderid)

    total = 0
    total_quantity = 0

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT SUM(quantity * product_price) AS total, SUM(quantity) AS total_quantity FROM InputHistory_inputorderitem WHERE inputOrder_id = %s",
            [orderid]
        )
        row = cursor.fetchone()

        if row:
            total, total_quantity = row

    context = {
        'order': inputOrder,
        'totalPrice': round(total, 2),
        'totalQuantity': total_quantity
    }
    return render(request, 'inputHistory-details.html', context)


from django.db import connection

@login_required(login_url='login')
def inputOrderEdit(request, orderid):
    if request.method == 'POST':
        order = get_object_or_404(InputOrder, id=orderid)
        is_external = request.POST.get("external")

        order.isExternal = True if is_external == "on" else False
        if request.POST.get("date") != '':
            date = request.POST["date"] + "-00:00:00"
            order.date_created = datetime.strptime(date, '%Y-%m-%d-%H:%M:%S')
            order.save()

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM InputHistory_inputorderitem WHERE inputOrder_id = %s",
                [orderid]
            )

        for i in range(1, len(request.POST) // 2):
            try:
                product_name = request.POST[f"product{i}"]
                quantity = request.POST[f"quantity{i}"]
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM ProductProduct WHERE name ILIKE %s",
                        [f"%{product_name}%"]
                    )
                    product_row = cursor.fetchone()
                    if product_row:
                        product_id = product_row[0]
                        cursor.execute(
                            "INSERT INTO InputHistory_inputorderitem (quantity, product_id, inputOrder_id) VALUES (%s, %s, %s)",
                            [quantity, product_id, orderid]
                        )
            except:
                pass

        return redirect('inputHistory')

    order = get_object_or_404(InputOrder, id=orderid)
    all_products = Product.objects.all()

    context = {
        'order': order,
        'allProducts': all_products,
    }

    return render(request, 'inputHistory-edit.html', context)



from django.db import connection

@login_required(login_url="login")
def deleteOrder(request):
    if request.method == "POST":
        order_id = int(request.POST["orderid"])

        with connection.cursor() as cursor:
            
            cursor.execute("""
                UPDATE Products_product p
                SET quantity = quantity - subquery.total_quantity
                FROM (
                    SELECT product_id, SUM(quantity) AS total_quantity
                    FROM InputHistory_inputorderitem
                    WHERE inputOrder_id = %s
                    GROUP BY product_id
                ) AS subquery
                WHERE p.id = subquery.product_id;
            """, [order_id])

            
            cursor.execute(
                "DELETE FROM InputHistory_inputorderitem WHERE inputOrder_id = %s",
                [order_id]
            )

           
            cursor.execute(
                "DELETE FROM InputHistory_inputorder WHERE id = %s",
                [order_id]
            )

        return JsonResponse({
            'success': True,
        })

    return JsonResponse({
        'success': False,
    })

