from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
import json
from django.views.decorators.http import require_POST
from django.db import transaction
from OutputHistory.models import OutputOrder, OutputOrderItem, Worker, Product
from django.contrib import messages


def store(request):
    if not request.session.get('employee_number'):
        return redirect('verify_employee')  # Redirect to the verification view
    query = request.GET.get('query', '')
    category = request.GET.get('category', '')

    products = Product.objects.filter(Q(name__icontains=query))

    if category:
        products = products.filter(category=category)

    context = {
        "products": products,
        "product_count": products.count(),
        "query": query,
        "categories": Product._meta.get_field('category').choices,  # Get category choices directly from the model field
        "selected_category": category,
    }

    return render(request, 'store/store.html', context)


def verify_employee(request):
    if request.method == 'POST':
        employee_number = request.POST.get('employee_number')
        password = request.POST.get('password')

        if not employee_number or not password:
            messages.error(request, 'Favor de ingresar ambos campos.')
            return redirect('verify_employee')

        try:
            worker = Worker.objects.get(employeeNumber=employee_number)
            if worker.employeePassword == password:
                # Password matches, proceed to the store
                request.session['employee_number'] = worker.employeeNumber  # Store employee number in session
                return redirect('store')
            else:
                # Password does not match
                messages.error(request, 'Contraseña no valida.')
                return redirect('verify_employee')
        except Worker.DoesNotExist:
            # Employee number does not exist
            messages.error(request, 'Numero de empleado no existe.')
            return redirect('verify_employee')

    return render(request, 'verify_employee.html')


def logout_worker(request):
    # This will clear the session
    request.session.flush()
    # Redirect to the login page or any other page
    return redirect('verify_employee')  # Replace 'verify_employee' with the name of your login view


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))  # Get quantity from POST request
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    request.session['cart'] = cart
    return redirect('store')  # Redirect back to the same page


def show_cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [(product, cart[str(product.id)]) for product in products]
    print(len(cart_items))
    context = {
        'cart_items': cart_items,
        'employee_number': request.session.get('employee_number'), }
    return render(request, 'store/cart.html', context)


def view_cart(request):
    # Check if the user is logged in by looking for 'employee_number' in the session
    if not request.session.get('employee_number'):
        # If not logged in, redirect to the login page
        return redirect('verify_employee')
    cart = request.session.get('cart', {})
    product_ids = list(map(int, cart.keys()))
    products = Product.objects.filter(id__in=product_ids)
    cart_items = []
    total = 0
    for product in products:
        quantity = cart[str(product.id)]
        total += product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity,
        })

    employee_number = request.session.get('employee_number')
    worker = Worker.objects.get(employeeNumber=employee_number)
    context = {
        'cart_items': cart_items,
        'total': total,
        'cart_count': len(cart_items),
        'worker_name': worker.name,
    }
    context.update({'employee_number': request.session.get('employee_number')})
    return render(request, 'store/cart.html', context)


@csrf_exempt
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
        total = calculate_cart_total(request)
        return JsonResponse({'total': total})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def calculate_cart_total(request):
    cart = request.session.get('cart', {})
    product_ids = list(map(int, cart.keys()))
    products = Product.objects.filter(id__in=product_ids)
    total = sum(product.price * cart[str(product.id)] for product in products)
    return total


@require_POST
def confirm_order(request):
    employee_number = request.POST.get('employee_number')
    order_items_json = request.POST.get('order_items')
    order_items = json.loads(order_items_json)

    worker = get_object_or_404(Worker, employeeNumber=employee_number)

    with transaction.atomic():
        output_order = OutputOrder(worker=worker)

        # primero hay que checar que haya suficiente disponibilidad para cada producto antes de crear la orden o items.

        # creamos un array de outputorderitems temporal
        tempOOItems = []

        for item in order_items:
            product = get_object_or_404(Product, id=item['productId'])
            quantity = int(item['quantity'])

            # Check if enough inventory (quantity) is available
            if product.quantity < quantity:
                return HttpResponseBadRequest(f'No hay suficientes disponibles para {product.name}')

            # Update the inventory quantity
            product.quantity -= quantity
            product.save()

            tempOOItems.append(OutputOrderItem(
                product=product,
                quantity=quantity,
                outputOrder=output_order
            ))
        output_order.save()
        for tempItem in tempOOItems:
            tempItem.save()

        if 'cart' in request.session:
            del request.session['cart']

        # After confirming the order, log out the user
    request.session.flush()  # Clears the session data

    # Optionally, return a response that triggers a client-side redirection
    return JsonResponse({'message': 'Orden confirmada!', 'logged_out': True})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


def order_history(request):
    return HttpResponse('aaaa')
