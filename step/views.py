from django.shortcuts import render,get_object_or_404
from.models import Supplier,Business,Customer,Products,Purchase,sells,expenses,notifications,Transactions,mode_of_payment
from .forms import SupplierForm,Businessform,CustomerForm,testform,ProductForm,PurchaseForm,SellForm,ExpenseForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Sum
from django.db.models import Q
import requests
from requests.auth import HTTPBasicAuth
import datetime
import json
import base64
from erp import settings
from .daraja import initiate_stk_push
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from.signals import stk_push_success
from django.dispatch import receiver

# Create your views here.
#main styling
def index(request):
    return render(request,'step/index2.html')

def home(request):
    user = request.user
    total_sales =sells.objects.filter(user=request.user).aggregate(total_sales=Sum('Amount_due'))['total_sales']
    total_expenses = expenses.objects.filter(user=request.user).aggregate(total_expenses=Sum('amount_to_bepaid'))['total_expenses']
    profit = total_sales
    if total_expenses and total_sales == int:
        profit = total_sales - total_expenses
       


    return render(request,"step/home.html",{"user":user,"sales":total_sales,"profit":profit,"expenses":total_expenses})



#used to run test

def test(request):
    return render(request,"step/test.html",{"form":testform})



#used to show all the suppliers
@login_required()
def supplier(request):
     #get all the business the user owns
     user_businesses = request.user.business_set.all()
     #retrieve all the suppliers associated with the users business
     suppliers = Supplier.objects.filter(business__in=user_businesses)

     return render(request,'step/suppliers.html',{'suppliers':suppliers})


@login_required()
def notify(request):
     #get all the business the user owns
     #retrieve all the suppliers associated with the users business
     notification = notifications.objects.filter(user=request.user)

     return render(request,'step/notification.html',{'notifications':notification})


#used to show all the customers
def customers(request):

    user_customer = request.user.business_set.all()
    
    customers = Customer.objects.filter(business__in=user_customer)

    return render(request,'step/customer.html',{'customers':customers})

#used to show all the products
def products(request):
     products = Products.objects.filter(user=request.user)
     return render(request,'step/products.html',{"products":products})

def purchase(request):
    purchase = Purchase.objects.filter(user=request.user)
    return render(request,'step/purchase.html',{"purchases":purchase})

def sales(request):
    sales = sells.objects.filter(user=request.user)
    return render(request,'step/sales.html',{'sales':sales})

@login_required()
def expenses1(request):
    expense = expenses.objects.filter(user=request.user)
    
    return render(request,'step/expenses.html',{"expenses":expense})

def view_transaction(request):
     transactions = Transactions.objects.filter(sellid__user=request.user)
     cash_total =Transactions.objects.filter(sellid__user=request.user ,mode_of_payment__id=1).aggregate(total=Sum('Amount_paid'))['total']
     mpesa_total =Transactions.objects.filter(sellid__user=request.user , mode_of_payment__id=2).aggregate(total=Sum('Amount_paid'))['total']
     return render(request,'step/transactions.html',{"transactions":transactions,"cash_total":cash_total,"mpesa_total":mpesa_total})




#VIEWS FOR ADDING 

#used to add new customers 
@login_required()
def add_customer(request):
    #check if user is logged in

    if request.user.is_authenticated:
        if request.method=='POST':
            form = CustomerForm(request.POST)
            if form.is_valid():
                form.save()

                return render(request,'step/add_customers.html',{'form':CustomerForm, 'success':True})
        else:
            user_business = Business.objects.filter(user=request.user)
            form = CustomerForm(initial={'business': user_business.first()})
            return render(request,'step/add_customers.html',{'form':form})


@login_required()
def add_purchase(request):
    if request.user.is_authenticated:
     if request.method=='POST':
        form = PurchaseForm(request.POST)

        if form.is_valid():
            new_purchase = form.save(commit=False)
            new_purchase.user=request.user

            #Get the product the purchase is made for a
            product_purchased = new_purchase.product
            #Get the quantity of the product purchased 
            quantity_purchased = new_purchase.quantity

            print(quantity_purchased)
            #Get the product quatinty for the product purchases
            update_quantity = Products.objects.get(pk=product_purchased.pk)

            update_quantity.stock += quantity_purchased

            update_quantity.save()
            

           
           


            new_purchase.save()

            return render(request,'step/add_purchases.html',{"form":PurchaseForm(),"success":True})
     else:

        return render(request,'step/add_purchases.html',{"form":PurchaseForm()})



@login_required()
def add_sales(request):
    if request.method == 'POST':
        form = SellForm(request.POST)

        if form.is_valid():
            new_sales = form.save(commit=False)
            new_sales.user =request.user

            product_sold = new_sales.Product_sold 
            quantity_sold = new_sales.quantity_sold
            

            products = Products.objects.get(pk=product_sold.pk)

            products.stock -= quantity_sold
           
            if quantity_sold > products.stock:
               return render(request,'step/add_sales.html',{"form":SellForm(),"fail":True})



            products.save()
            new_sales.save()
            sell_id = new_sales.id
           

                

            return HttpResponseRedirect(reverse('transaction', args=[sell_id]))
    else:
         return render(request,'step/add_product.html',{"form":SellForm()})



@login_required()
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)

        if form.is_valid():
           expense = form.save(commit=False)
           expense.user = request.user
           expense.save()

           return render(request,'step/add_expenses.html',{"form":ExpenseForm(),"success":True})
    return render(request,'step/add_expenses.html',{"form":ExpenseForm()})
    





#used to add suppliers 
@login_required()
def add_supplier(request):

   if request.user.is_authenticated:
     if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
           new_supplier = form.save(commit=False)
           if request.user.business_set.exists():
                new_supplier.business = request.user.business_set.first()
                new_supplier.save() 

                return render(request, 'step/add_suppliers.html', {'form': SupplierForm(), 'success': True})

     else:
        user_businesses = Business.objects.filter(user=request.user)
        form = SupplierForm(initial={'business': user_businesses.first()}) # Corrected instantiation of the form
        return render(request, 'step/add_suppliers.html', {'form': form})
     

#used to add products
@login_required()
def add_product(request):
    if request.user.is_authenticated:
        if request.method =='POST':
        
            form = ProductForm(request.POST,request.FILES)
            if form.is_valid():
               new_product=form.save(commit=False)
               new_product.user=request.user
               new_product.save()
               return render(request,'step/add_product.html',{"form":form,"success":True})
            return render(request, 'step/add_product.html', {"form": form})

    return render(request,'step/add_product.html',{"form":ProductForm()})

#used to add businesses 
@login_required()
def add_business(request):
    if request.method == 'POST':
        form = Businessform(request.POST)
        if form.is_valid():
             new_business=form.save(commit=False)
             new_business.user = request.user  # Associate with logged-in user
             new_business.save()        

             return render(request,'step/add_business.html',{'form':form})
    else:
        form = Businessform
        return render(request,'step/add_business.html',{'form':form})
    

#need to fic this
def delete(request,id):
    if request=='POST':
        s = Customer.objects.get(pk=id)
        s.delete()
        
        user_customer = request.user.business_set.all()
        customers = Customer.objects.filter(business__in=user_customer)
        return render(render,'step/customer.html',{"customers":customers})
    else:
      return HttpResponseRedirect(reverse('customer'))


def edit(request,id):
    if request.method=='POST':
       customer = Customer.objects.get(pk=id)
       form=CustomerForm(request.POST,instance=customer)
       if form.is_valid():
           form.save()

           return render(request,'step/customer_edit.html',{"form":form})
    else:
       customer = Customer.objects.get(pk=id)
       form = CustomerForm(instance=customer)
       return render(request, 'step/customer_edit.html', {
    'form': form
    })




#Logic to solve my problems
def delete(model,id):
    if model==0:
        customer = Customer.objects.get(pk=id)
        customer.delete()
        return HttpResponseRedirect(reverse('customer'))

    elif model==1:
        customer = Supplier.objects.get(pk=id)
        customer.delete()
        return HttpResponseRedirect(reverse('supplier'))
    elif model==2:
        customer = Products.objects.get(pk=id)
        customer.delete()
        return HttpResponseRedirect(reverse('products'))
    elif model==3:
        customer = Purchase.objects.get(pk=id)
        customer.delete()
        return HttpResponseRedirect(reverse('purchase'))
    elif model==4:
        customer = expenses.objects.get(pk=id)
        customer.delete()
        return HttpResponseRedirect(reverse('expenses'))
    elif model==5:
        customer = sells.objects.get(pk=id)
        customer.delete()
        return HttpResponseRedirect(reverse('sales'))
   
   
   
    return -0        












def delete_customer(request,model,id):
    if request.method=='POST':
        return delete(model,id)
        


def search(request):
    query = request.GET.get('query')
    results = []
    if query:
        results = Customer.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) 
        )
    return render(request, 'step/customer.html', {'results': results, 'query': query})


#pass the id in future things 

def transaction(request,id):
    sale = sells.objects.get(id=id)
    
    
    
    
        
    if request.method=='POST':
        zd = sale.mode_of_payment
        Amount = int(request.POST.get('amount'))
        phonenumber = request.POST.get('phoneNumber')
       
        if 'mpesa' in request.POST:
            initiate_stk_push(Amount,phonenumber)
            zd=2
            mode_of_payment_instance = get_object_or_404(mode_of_payment, id=zd)
        
            transaction = Transactions(
              sellid=sale,
            mode_of_payment=mode_of_payment_instance,
            Amount_paid=Amount
               )
            transaction.save()
            return HttpResponseRedirect(reverse('sales'))

        else:
     
         
         zd = 1
         mode_of_payment_instance = get_object_or_404(mode_of_payment, id=zd)
        
         transaction = Transactions(
              sellid=sale,
            mode_of_payment=mode_of_payment_instance,
            Amount_paid=Amount
         )
         transaction.save()
       
         return HttpResponseRedirect(reverse('sales'))
    
    else:
      
       totals = sells.objects.get(id=id)
       total = totals.Amount_due
       Amount_paid = totals.Amount_paid

       return render(request, 'step/add_transaction.html',{"total":total,"paid":Amount_paid})

      
    

    
    
    
    
   




def pos(request):

    return render(request, 'step/pos.html')




@csrf_exempt
def mpesa_callback(request):
        if request.method == 'POST':
         data = request.json
        # Process the callback data here
        # You can save the data to the database or perform other actions
         print(f"Callback data: {data}")
        # Extract the necessary information from the callback data
         callback_data = data.get('Body').get('stkCallback')
         merchant_request_id = callback_data.get('MerchantRequestID')
         checkout_request_id = callback_data.get('CheckoutRequestID')
         result_code = callback_data.get('ResultCode')
         result_desc = callback_data.get('ResultDesc')
         amount = None
         mpesa_receipt_number = None
         transaction_date = None
         phone_number = None

         return JsonResponse({"status": "success"})
        return JsonResponse({"status":"denied"})
   










#DARAJA API CODE BELOW














