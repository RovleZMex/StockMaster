import unicodedata
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.db import connection

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
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM OutputOrder WHERE id = %s", [orderid])
        order = cursor.fetchone()

    if request.method == "POST":
        form_data = request.POST

        worker_id_query = "SELECT id FROM Worker WHERE name = %s"
        cursor.execute(worker_id_query, [form_data.get("nameWorker")])
        worker_id = cursor.fetchone()[0]

        update_order_query = "UPDATE OutputOrder SET worker_id = %s, date_created = %s WHERE id = %s"
        cursor.execute(update_order_query, [worker_id, form_data.get("dateCreation"), orderid])

        cursor.execute("SELECT * FROM OutputOrderItem WHERE outputOrder_id = %s", [orderid])
        product_items = cursor.fetchall()

        for product_item in product_items:
            quantity_key = f"quantityProduct_{product_item[1]}"  # assuming product_id is at index 1
            new_quantity = int(form_data.get(quantity_key, 0))
            old_quantity = product_item[2]  # assuming quantity is at index 2

            cursor.execute("UPDATE Product SET quantity = quantity - %s WHERE id = %s", [new_quantity - old_quantity, product_item[1]])
            cursor.execute("UPDATE OutputOrderItem SET quantity = %s WHERE product_id = %s AND outputOrder_id = %s", [new_quantity, product_item[1], orderid])

            if new_quantity == 0:
                cursor.execute("DELETE FROM OutputOrderItem WHERE product_id = %s AND outputOrder_id = %s", [product_item[1], orderid])

        new_product_names = form_data.getlist('newProductName[]')
        new_product_quantities = form_data.getlist('newProductQuantity[]')

        for name, quantity in zip(new_product_names, new_product_quantities):
            if name:
                cursor.execute("SELECT id, quantity FROM Product WHERE name = %s", [name])
                existing_product = cursor.fetchone()
                if existing_product:
                    existing_item_query = "SELECT id FROM OutputOrderItem WHERE product_id = %s AND outputOrder_id = %s"
                    cursor.execute(existing_item_query, [existing_product[0], orderid])
                    existing_item = cursor.fetchone()

                    if existing_item:
                        cursor.execute("UPDATE OutputOrderItem SET quantity = quantity + %s WHERE product_id = %s AND outputOrder_id = %s", [int(quantity), existing_product[0], orderid])
                        cursor.execute("UPDATE Product SET quantity = quantity - %s WHERE id = %s", [int(quantity), existing_product[0]])
                    else:
                        cursor.execute("INSERT INTO OutputOrderItem (product_id, quantity, outputOrder_id) VALUES (%s, %s, %s)", [existing_product[0], quantity, orderid])
                        cursor.execute("UPDATE Product SET quantity = quantity - %s WHERE id = %s", [int(quantity), existing_product[0]])
                else:
                    cursor.execute("INSERT INTO Product (name, quantity) VALUES (%s, 0)", [name])
                    new_product_id = cursor.lastrowid
                    cursor.execute("INSERT INTO OutputOrderItem (product_id, quantity, outputOrder_id) VALUES (%s, %s, %s)", [new_product_id, quantity, orderid])
                    cursor.execute("UPDATE Product SET quantity = quantity - %s WHERE id = %s", [int(quantity), new_product_id])

        return redirect('outputDetails', orderid)

    context = {
        "order": order,
        "id": orderid,
        "workers": Worker.objects.raw("SELECT * FROM Worker"),
        "products": Product.objects.raw("SELECT * FROM Product"),
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

def deleteOrderOutput(request):
    if request.method == "POST":
        id = int(request.POST["orderid"])

        with connection.cursor() as cursor:
            cursor.execute("SELECT product_id, quantity FROM OutputOrderItem WHERE outputOrder_id = %s", [id])
            items = cursor.fetchall()
            for item in items:
                cursor.execute("UPDATE Product SET quantity = quantity + %s WHERE id = %s", [item[1], item[0]])
            cursor.execute("DELETE FROM OutputOrder WHERE id = %s", [id])

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
        isExternal = request.POST.get("external")

        order.isExternal = True if isExternal == "on" else False
        if request.POST.get("date") != '':
            date = request.POST["date"] + "-00:00:00"
            order.date_created = datetime.strptime(date, '%Y-%m-%d-%H:%M:%S')
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
