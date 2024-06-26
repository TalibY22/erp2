from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user





class Business(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)  # Foreign key to User
    business_name = models.CharField(max_length=200)
    # ... Other business fields

    def __str__(self):
        return self.business_name
    

class Business_location(models.Model):
    location = models.CharField(max_length=200)
    phone_number  = models.IntegerField()






class Supplier(models.Model):
    business = models.ForeignKey(Business,on_delete=models.CASCADE,null=True)
    supplier_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200)
   

    def __str__(self) -> str:
        return f'supplier {self.supplier_name}'










class Customer(models.Model):
    business = models.ForeignKey(Business,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200)
    opening_credit = models.IntegerField(default=0)
   

    def __str__(self) -> str:
        return f'customer  {self.first_name}'
    
#THe fuck why are u not wo
class Products(models.Model):
      user = models.ForeignKey(User,on_delete=models.CASCADE)
      product_name=models.CharField(max_length=200)
      supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE)
      Buying_price = models.IntegerField()
      selling_price = models.IntegerField()
      alert_quantity = models.IntegerField(default=3)
      stock = models.IntegerField(null=False)
      product_picture = models.ImageField(upload_to='images/',null=True)

      def __str__(self) -> str:
        return  self.product_name

class Status(models.Model):
    status=models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.status



class Purchase(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    Buying_price = models.IntegerField()
    date=models.DateTimeField(auto_now_add=True,null=True)
    status=models.ForeignKey(Status,on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def delete(self, *args, **kwargs):
        #u calling the primary  model referencing the stock level  and telling it to delete
        self.product.stock -= self.quantity
        #Then call the save method to save the initial method 
        self.product.save()
        
        
        super().delete(*args, **kwargs)



class payment_status(models.Model):
      status=models.CharField(max_length=255)

      def __str__(self) -> str:
          return self.status



class mode_of_payment(models.Model):
    payment_mode=models.CharField(max_length=11)

    def __str__(self) -> str:
        return self.payment_mode


class sells(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    Product_sold = models.ForeignKey(Products,on_delete=models.CASCADE)
    mode_of_payment=models.ForeignKey(mode_of_payment,on_delete=models.CASCADE)
    quantity_sold=models.IntegerField()
    Amount_due = models.IntegerField()
    Amount_paid = models.IntegerField(default=0)
    Payment_status=models.ForeignKey(payment_status,on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        #if there is product sold and quantity sold``
        if self.Product_sold and self.quantity_sold:
            #times the products selling price * the quantity
            self.Amount_due = self.Product_sold.selling_price * self.quantity_sold
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        #u calling the primary  model referencing the stock level  and telling it to delete
        self.Product_sold.stock += self.quantity_sold
        #Then call the save method to save the initial method 
        self.Product_sold.save()
        
        
        super().delete(*args, **kwargs)
    def __str__(self) -> str:
        return self.customer.first_name



   

class Expense_category(models.Model):
      category = models.CharField(max_length=200)

      def __str__(self) -> str:
          return self.category

class expenses(models.Model):
      user = models.ForeignKey(User,on_delete=models.CASCADE)
      expense_category = models.ForeignKey(Expense_category,on_delete=models.CASCADE)
      amount_to_bepaid = models.IntegerField()
      amount_paid = models.IntegerField()



class notifications(models.Model):
      user = models.ForeignKey(User,on_delete=models.CASCADE)
      Message = models.TextField()
      timestamp = models.DateTimeField(auto_now_add=True)
      






class Transactions(models.Model):
      sellid=models.ForeignKey(sells,on_delete=models.CASCADE)
      mode_of_payment=models.ForeignKey(mode_of_payment,on_delete=models.CASCADE)
      Amount_paid = models.IntegerField()
      date_paid = models.DateTimeField(auto_now_add=True)

      def save(self, *args, **kwargs):
        #if there is product sold and quantity sold``
        amount_due = self.Amount_paid - self.sellid.Amount_due
        
        if self.Amount_paid >= self.sellid.Amount_due:
            self.sellid.Amount_paid=self.Amount_paid
            self.sellid.Payment_status = payment_status.objects.get(status='Paid')  # Assuming 'Paid' status exists
        else:
            self.sellid.Amount_paid = self.Amount_paid 
            self.sellid.Payment_status = payment_status.objects.get(status='Partial')  # Assuming 'Partial Payment' status exists
        
        self.sellid.save()
        super().save(*args, **kwargs)
         




class test(models.Model):
    pic = models.ImageField()






    

