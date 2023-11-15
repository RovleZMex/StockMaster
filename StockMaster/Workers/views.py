from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
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
    context = {'cart_items': cart_items, 'employee_number': request.session.get('employee_number')}
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
    context = {
        'cart_items': cart_items,
        'total': total,
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

    # Retrieve the worker by employee number
    worker = get_object_or_404(Worker, employeeNumber=employee_number)

    # Start a database transaction
    with transaction.atomic():
        # Create a new OutputOrder
        output_order = OutputOrder(worker=worker)
        output_order.save()

        # Create OutputOrderItem instances for each item in the order
        for item in order_items:
            product = get_object_or_404(Product, id=item['productId'])
            quantity = item['quantity']
            OutputOrderItem.objects.create(
                product=product,
                quantity=quantity,
                outputOrder=output_order
            )

            # Clear the cart from the session
        if 'cart' in request.session:
            del request.session['cart']
    return JsonResponse({'message': 'Orden confirmada!'})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})


