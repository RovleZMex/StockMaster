from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

'''
I wanted to prove that we can link orders with multiple products to a singular worker
With the use of a new model OutputOrder that stores the worker object, and a helper model
OutputOrderItem, this model stores a singular product and the quantity that was taken in this order,
and is linked to a OutputOrder. We can pin point a worker searching by name, or worker code with:

 >> worker = Worker.objects.get(name='Karl')
or 
 >> worker = Worker.objects.get(workerCode=935431)

We can then access all of the orders attached to a worker with:

 >> allOrders = OutputOrder.objects.filter(worker=worker)

allOrders will contain an array of OutputOrder models with all the orders attached to worker, to then access the items 
and quantities for each item in the order we can do it with:

 >> allItemsInOrder = allOrders[index].GetItems()
 
allItemsInOrder is an array of OutputOrderItem models, each of them contains a Product model, and quantity
for each, por example:

 >> allItemsInOrder[0].product.name -> "Esponja"
 >> allItemsInOrder[0].quantity -> 2

What that means is that Karl took 2 esponjas from the storage.

To create a new order we first have to create a Worker model, create a new OutputOrder and link it to the worker. 
Then we can create OutputOrderItem and link it to the OutputOrder just created.


| Worker 
    | OutputOrder  (A Worker can have multiple OutputOrders but the OutputOrder only one Worker)
        | OutputOrderItem (A OutputOrder can have multiple OutputOrderItems but the OutputOrderItems only one OutputOrder)
                          (A Product can have multiple OutputOrderItems but the OutputOrderItem only one Product)
            | Product 
'''


# Create your views here.

@login_required(login_url='login')
def history(request):
    return render(request, 'outputHistoryWorker.html')

@login_required(login_url='login')
def outputHistory(request):
    return render(request, 'outputHistory.html')

@login_required(login_url='login')
def inputHistory(request):
    return render(request, 'inputHistory.html')
