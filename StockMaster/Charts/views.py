import calendar
import json
from datetime import date, datetime
# HTML??
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

from InputHistory.models import InputOrder
from Product.models import Product


#######

def render_to_pdf(template_src, contextDict):
    template = get_template(template_src)
    html = template.render(contextDict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')


class ViewPDF(View):
    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            month = int(request.POST.get("month"))
            year = int(request.POST.get("year"))
            if int(request.POST.get("month")) != datetime.now().month or int(
                    request.POST.get("year")) != datetime.now().year:
                products = GetInventoryAsOfDate(date(year, month, calendar.monthrange(year, month)[1]))
                toDate = date(year, month, calendar.monthrange(year, month)[1])
            elif int(request.POST.get("month")) == datetime.now().month or int(
                    request.POST.get("year")) == datetime.now().year:
                products = Product.objects.all()
                toDate = datetime.now().date()
            else:
                products = []
                toDate = datetime.now().date()
            fromDate = date(year, month, 1)

            totalValue = round(sum([product.getTotalValue() for product in products]), 2)
            quantities = GetQuantPerCategory(products)
            catValues = [0, 0, 0, 0]
            for product in products:
                if product.category == "ELE":
                    catValues[0] += product.getTotalValue()
                elif product.category == "PLU":
                    catValues[1] += product.getTotalValue()
                elif product.category == "OFF":
                    catValues[2] += product.getTotalValue()
                elif product.category == "CLE":
                    catValues[3] += product.getTotalValue()

            context = {
                'products': products,
                'totalValue': totalValue,
                'date': datetime.now().date(),
                'fromDate': fromDate,
                'toDate': toDate,
                'categories': ["Eléctricos", "Plomería", "Oficina", "Limpieza"],
                'quantities': quantities,
                'percentages': [round((x * 100) / sum(quantities), 2) for x in quantities],
                'catValues': catValues,
            }
            pdf = render_to_pdf('inventoryTextTemplate.html', contextDict=context)
            return HttpResponse(pdf, content_type='application/pdf')


@login_required(login_url='login')
def ReportCharts(request):
    categories = ['Eléctrico', 'Plomería', 'Oficina', 'Limpieza']
    quantities = [0, 0, 0, 0]
    for product in Product.objects.all():
        if product.category == "ELE":
            quantities[0] += product.quantity
        elif product.category == "PLU":
            quantities[1] += product.quantity
        elif product.category == "OFF":
            quantities[2] += product.quantity
        elif product.category == "CLE":
            quantities[3] += product.quantity
    percentages = [round((x * 100) / sum(quantities), 2) for x in quantities]
    context = {
        'years': range(2023, datetime.now().year + 1),
        'quantities': json.dumps(quantities),
        'categories': ','.join(categories),
        'percentages': json.dumps(percentages),
    }
    return render(request, 'report-invCharts.html', context)


@login_required(login_url='login')
def GetStockMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        labels = []
        stock = []
        if datetime.now().month == month:
            daysRange = range(1, datetime.now().day + 1)
        elif month > datetime.now().month or year > datetime.now().year:
            daysRange = range(0)
        else:
            daysRange = range(1, calendar.monthrange(year, month)[1] + 1)
        for i in daysRange:
            dayTotal = 0
            labels.append(f"Día {i}")
            for product in Product.objects.all():
                product = product
                time = date(year, month, i)
                try:
                    dayTotal += product.history.as_of(time).quantity
                except ObjectDoesNotExist:
                    continue
            stock.append(dayTotal)
        return JsonResponse({
            'success': True,
            'data': json.dumps(stock),
            'labels': ','.join(labels),
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url="login")
def GetCategoriesMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        dateObj = date(year, month, calendar.monthrange(year, month)[1])
        historicInv = GetInventoryAsOfDate(dateObj)

        return JsonResponse({
            'success': True,
            'data': json.dumps(GetQuantPerCategory(historicInv))
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url="login")
def GetPercentagesMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        dateObj = date(year, month, calendar.monthrange(year, month)[1])
        historicInv = GetInventoryAsOfDate(dateObj)
        percentages = GetPercentagesPerCategory(historicInv)

        return JsonResponse({
            'success': True,
            'data': json.dumps(percentages)
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url='login')
def TextInventory(request):
    years = range(2023, datetime.now().year + 1)
    month = None
    if request.method == "POST":
        print("POSTIIIIIINGGGG")
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        if int(request.POST.get("month")) != datetime.now().month or int(
                request.POST.get("year")) != datetime.now().year:
            products = GetInventoryAsOfDate(date(year, month, calendar.monthrange(year, month)[1]))
        elif int(request.POST.get("month")) == datetime.now().month or int(
                request.POST.get("year")) == datetime.now().year:
            products = Product.objects.all()
        else:
            products = []
    else:
        products = Product.objects.all()
        month = datetime.now().month
        year = datetime.now().year

    percentages = GetPercentagesPerCategory(products)
    catQuantities = GetQuantPerCategory(products)

    catValues = [0, 0, 0, 0]

    for product in products:
        if product.category == "ELE":
            catValues[0] += product.getTotalValue()
        elif product.category == "PLU":
            catValues[1] += product.getTotalValue()
        elif product.category == "OFF":
            catValues[2] += product.getTotalValue()
        elif product.category == "CLE":
            catValues[3] += product.getTotalValue()

    categories = []

    for i in range(len(percentages)):
        categories.append([MapCategory(i), catQuantities[i], percentages[i], catValues[i]])

    context = {
        'years': years,
        'products': products,
        'totalQuant': sum([product.quantity for product in products]),
        'totalPrice': round(sum([product.getTotalValue() for product in products]), 2),
        'categories': categories,
        'month': int(month),
        'year': int(year),
    }
    return render(request, 'report-invText.html', context)


@login_required(login_url='login')
def TextExpense(request):
    years = range(2023, datetime.now().year + 1)
    month = None

    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        if month != datetime.now().month or year != datetime.now().year:
            orders = GetOrderAsOfDate(year, month)
        elif month == datetime.now().month or year == datetime.now().year:
            orders = GetOrderAsOfDate(year, month)
        else:
            orders = []
    else:
        month = datetime.now().month
        year = datetime.now().year
        orders = GetOrderAsOfDate(year, month)

    context = {
        'years': years,
        'orders': orders,
        'month': int(month),
        'year': int(year),
        'totalOrders': len(orders),
        'totalExpense': sum([order.GetTotal() for order in orders])
    }
    return render(request, 'report-expText.html', context)


def getTotalValueOrder(order):
    value = 0
    for item in order:
        value += item.getSubtotal()
    return value


def GetInventoryAsOfDate(dateA):
    inventory = []
    if dateA <= datetime.now().date() or dateA.month == datetime.now().month:
        for product in Product.objects.all():
            try:
                inventory.append(product.history.as_of(dateA))
            except ObjectDoesNotExist:
                pass
    return inventory


def GetPercentagesPerCategory(inventory):
    quantities = GetQuantPerCategory(inventory)
    if sum(quantities) != 0:
        percentages = [round((x * 100) / sum(quantities), 2) for x in quantities]
    else:
        percentages = [0, 0, 0, 0]
    return percentages


def GetQuantPerCategory(inventory):
    quantities = [0, 0, 0, 0]
    for product in inventory:
        if product.category == "ELE":
            quantities[0] += product.quantity
        elif product.category == "PLU":
            quantities[1] += product.quantity
        elif product.category == "OFF":
            quantities[2] += product.quantity
        elif product.category == "CLE":
            quantities[3] += product.quantity
    return quantities


def MapCategory(value):
    categories = ["Eléctricos", "Plomería", "Oficina", "Limpieza"]
    return categories[value]


def GetOrderAsOfDate(year, month):
    orders = []
    for order in InputOrder.objects.all().order_by('date_created'):
        if order.date_created.month == month and order.date_created.year == year:
            orders.append(order)
    return orders
