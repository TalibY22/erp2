from django.shortcuts import render
from.models import Supplier,Business,Customer,Products
from .forms import SupplierForm,Businessform,CustomerForm,testform,ProductForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.
#main styling
def index(request):
    return render(request,'step/index.html')



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

#used to show all the customers
def customers(request):

    user_customer = request.user.business_set.all()
    customers = Customer.objects.filter(business__in=user_customer)

    return render(request,'step/customer.html',{'customers':customers})

#used to show all the products
def products(request):
     products = Products.objects.all()
     return render(request,'step/products.html',{"products":products})





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
        
            form = ProductForm(request.POST)
            if form.is_valid():
               new_product=form.save(commit=False)
               new_product.user=request.user
               new_product.save()
               return render(request,'step/add_product.html',{"form":form(),"success":True})

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
        supplier = Supplier.objects.get(pk=id)
        supplier.delete()

        return HttpResponseRedirect(reverse('index'))
    
    return HttpResponseRedirect(reverse('supplier'))