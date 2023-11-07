from django.shortcuts import render, redirect, get_object_or_404
from Product.models import Product
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_POST



def store(request):
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


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))  # Get quantity from POST request
    if str(product_id) in cart:
        cart[str(product_id)] += quantity
    else:
        cart[str(product_id)] = quantity
    request.session['cart'] = cart
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'store'))  # Redirect back to the same page



def show_cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [(product, cart[str(product.id)]) for product in products]
    return render(request, 'store/cart.html', {'cart_items': cart_items})


def view_cart(request):
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

    # Constructing the order details string
    order_details = "Employee Number: {}\n".format(employee_number)
    order_details += "Products:\n"

    for item in order_items:
        product = Product.objects.get(id=item['productId'])
        quantity = item['quantity']
        order_details += "- {} ({}): {}\n".format(product.name, product.SKU, quantity)



    print(order_details)  # For demonstration, printing the order details to the console

    # Clear the cart
    if 'cart' in request.session:
        del request.session['cart']

    return HttpResponse('Orden confirmada!!!!!(Check console for details)')


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'store/product_detail.html', {'product': product})
