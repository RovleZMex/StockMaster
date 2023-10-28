from django.shortcuts import render,redirect
from Product.models import Product
from django.db.models import Q


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

    # Handle adding to cart
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        cart = request.session.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + 1
        request.session['cart'] = cart
        return redirect('store')

    # Get cart from session
    cart = request.session.get('cart', {})
    cart_items = []
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        cart_items.append({'product': product, 'quantity': quantity})

    context.update({
        'cart_items': cart_items,
    })
    return render(request, 'store/store.html', context)
