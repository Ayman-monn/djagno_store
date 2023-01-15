from django.contrib import admin
from store import models


@admin.register(models.Category) 
class CategoryAdmin(admin.ModelAdmin): 
    list_per_page = 20 


@admin.register(models.Author) 
class AuthorAdmin(admin.ModelAdmin) : 
    list_per_page =20 


@admin.register(models.Product) 
class ProductAdmin(admin.ModelAdmin): 
    list_per_page = 20 


@admin.register(models.Slider)
class SliderAdmin(admin.ModelAdmin): 
    list_per_page = 20 


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin): 
    list_select_related= ['transaction'] 
    list_per_page=20
    list_display=['id', 'email', 'amount', 'payment_method', 'items', 'created_at']

    def has_change_permission(self, request, obj=None): 
        return False 

    def has_add_permission(self, request): 
        return False 
    
    def amount(self, obj):
        if obj.transaction is None: 
            return 0  
        return obj.transaction.amount

    def items(self, obj): 
        if obj.transaction is None:
            return {} 
        return len(obj.transaction.items) 
    
    def email(self, obj): 
        if obj.transaction is None: 
            return ''
        return obj.transaction.customer_email  
    
    def payment_method(self, obj): 
        if obj.transaction is None: 
            return ''
        return obj.transaction.get_paymentmethod_display()
