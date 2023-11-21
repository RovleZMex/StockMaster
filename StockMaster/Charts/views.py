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


class ViewExpPDF(View):
    def get(self, request, *args, **kwargs):
        return render(request, "error.html", {"message": "Por favor genera un nuevo PDF"})

    def post(self, request, *args, **kwargs):
        month = int(request.POST.get("month"))
        year = int(request.POST.get("year"))
        if int(request.POST.get("month")) != datetime.now().month or int(
                request.POST.get("year")) != datetime.now().year:
            orders = GetOrderAsOfDate(year, month)
            toDate = date(year, month, calendar.monthrange(year, month)[1])
        elif int(request.POST.get("month")) == datetime.now().month or int(
                request.POST.get("year")) == datetime.now().year:
            orders = GetOrderAsOfDate(year, month)
            toDate = datetime.now().date()
        else:
            orders = []
            toDate = datetime.now().date()
        fromDate = date(year, month, 1)
        percentages = getExpensesPercentagesPerCategory(orders)
        catQuantities = getExpensesPerCategory(orders)
        tempProducts = []

        class TempProduct:
            def __init__(self, product, sku, quantity=0, total=0):
                self.sku = sku
                self.name = product.name
                self.quantity = quantity
                self.total = total

            def __eq__(self, other):
                """Overrides the default implementation"""
                if isinstance(other, TempProduct):
                    return self.name == other.name
                return False

        for order in orders:
            for item in order.inputorderitem_set.all():
                tempProduct = TempProduct(item.product, item.product.SKU)
                if tempProduct in tempProducts:
                    tempProducts[tempProducts.index(tempProduct)].quantity += item.quantity
                    tempProducts[tempProducts.index(tempProduct)].total += item.getSubtotal()
                else:
                    tempProduct.quantity = item.quantity
                    tempProduct.total = item.getSubtotal()
                    tempProducts.append(tempProduct)
        context = {
            'orders': orders,
            'date': datetime.now().date(),
            'totalExpense': round(sum([order.GetTotal() for order in orders]), 2),
            'fromDate': fromDate,
            'toDate': toDate,
            'percentages': percentages,
            'catQuantities': catQuantities,
            'products': tempProducts,
        }
        pdf = render_to_pdf('expensesTextTemplate.html', contextDict=context)
        return HttpResponse(pdf, content_type='application/pdf')


@login_required(login_url="login")
def ExpensesCharts(request):
    context = {
        'years': range(2023, datetime.now().year + 1)
    }
    return render(request, 'report-expCharts.html', context)


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
                    if datetime.now().day == i and datetime.now().month == month and datetime.now().year == year:
                        dayTotal += product.quantity
                    else:
                        dayTotal += product.history.as_of(time).quantity
                except ObjectDoesNotExist:
                    pass
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


@login_required(login_url='login')
def GetExpensesPerCategoryMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        orders = getOrdersInMonthAndYear(month, year)
        quantities = getExpensesPerCategory(orders)
        return JsonResponse({
            'success': True,
            'data': json.dumps(quantities),
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url='login')
def GetExpensesPercentages(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        orders = getOrdersInMonthAndYear(month, year)
        percentages = getExpensesPercentagesPerCategory(orders)
        return JsonResponse({
            'success': True,
            'data': json.dumps(percentages)
        })
    else:
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
def GetExpensesMonth(request):
    if request.method == "POST":
        year = int(request.POST.get("year"))
        month = int(request.POST.get("month"))
        orders = getOrdersInMonthAndYear(month, year).order_by("date_created")
        print(orders)

        # Obtener todas las fechas del mes
        allDates = [datetime(year, month, day).date() for day in range(1, calendar.monthrange(year, month)[1] + 1)]

        # Inicializar el diccionario de totales
        expenses = {dictDate: 0 for dictDate in allDates}

        cumulativeTotal = 0
        for order in orders:
            temp_date = order.date_created.date()
            cumulativeTotal += order.GetTotal()
            expenses[temp_date] = cumulativeTotal

        # Fill missing days with existing data
        for i in range(1, len(allDates)):
            if expenses[allDates[i]] == 0:
                # If total is 0, set total as closest value
                j = i - 1
                while j >= 0 and expenses[allDates[j]] == 0:
                    j -= 1
                if j >= 0:
                    expenses[allDates[i]] = expenses[allDates[j]]

        # Create labels and totals for sending to frontend
        labels = [f"Día {dictDate.day}" for dictDate in allDates]
        totals = [expenses[dictDate] for dictDate in allDates]

        return JsonResponse({
            'success': True,
            'data': json.dumps(totals),
            'labels': ','.join(labels)
        })
    return JsonResponse({
        'success': False,
    })


@login_required(login_url='login')
def TextInventory(request):
    years = range(2023, datetime.now().year + 1)
    month = None
    if request.method == "POST":
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

        # valorProductos = []
        #
        # for product in products:
        #     lista = product.inputorderitem_set.all()
        #     totalCostoItem = 0
        #     for item in lista:
        #         item.inputOrder.date_created ? mes
        #         y
        #         año
        #         totalCostoItem += item.getSubtotal()
        #     valorProductos.append(totalCostoItem)

        valorProductos = {}
        totalProductos = 0  # Variable para almacenar la cantidad total de productos

        for product in products:
            lista = product.inputorderitem_set.filter(inputOrder__date_created__year=year,
                                                      inputOrder__date_created__month=month)
            totalCostoItem = 0
            totalProductosItem = 0  # Variable para almacenar la cantidad total de productos por producto

            for item in lista:
                totalCostoItem += item.getSubtotal()
                totalProductosItem += item.quantity  # Asumiendo que hay un campo quantity en tu modelo de item

            if totalCostoItem > 0:
                valorProductos[product.name] = {
                    'cantidad_total_productos': totalProductosItem,
                    'costo_total': totalCostoItem,
                }
                totalProductos += totalProductosItem  # Sumar la cantidad total de productos

        # Ordenar el diccionario por el valor de los costos totales de mayor a menor
        valorProductosOrdenado = dict(
            sorted(valorProductos.items(), key=lambda item: item[1]['costo_total'], reverse=True))

        # Resto de tu lógica para renderizar la plantilla con el contexto...

        context = {
            'years': years,
            'orders': orders,
            'month': int(month),
            'year': int(year),
            'totalOrders': len(orders),
            'totalExpense': round(sum([order.GetTotal() for order in orders]), 2),
            'valorProductosOrdenado': valorProductosOrdenado,
            'totalProductos': totalProductos,
        }
    return render(request, 'report-expText.html', context)


def getExpensesPerCategory(orders):
    quantities = [0, 0, 0, 0]
    for order in orders:
        for productItem in order.inputorderitem_set.all():
            if productItem.product.category == "ELE":
                quantities[0] += productItem.getSubtotal()
            elif productItem.product.category == "PLU":
                quantities[1] += productItem.getSubtotal()
            elif productItem.product.category == "OFF":
                quantities[2] += productItem.getSubtotal()
            elif productItem.product.category == "CLE":
                quantities[3] += productItem.getSubtotal()
    return quantities


def getOrdersInMonthAndYear(month, year):
    return InputOrder.objects.filter(date_created__month=month,
                                     date_created__year=year)


def GetInventoryAsOfDate(dateA):
    inventory = []
    if dateA <= datetime.now().date() or dateA.month == datetime.now().month:
        for product in Product.objects.all():
            try:
                inventory.append(product.history.as_of(dateA))
            except ObjectDoesNotExist:
                pass
    return inventory


def getExpensesPercentagesPerCategory(orders):
    quantities = getExpensesPerCategory(orders)
    if sum(quantities) != 0:
        percentages = [round((x * 100) / sum(quantities), 2) for x in quantities]
    else:
        percentages = [0, 0, 0, 0]
    return percentages


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
    for order in InputOrder.objects.all().order_by('-date_created'):
        if order.date_created.month == month and order.date_created.year == year:
            orders.append(order)
    return orders
