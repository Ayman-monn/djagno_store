import math
from django.shortcuts import render, redirect 
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from .froms import UserInfoFrom, MyPayPalPaymentsForm 
from store.models import Product, Cart
from django_store import settings 
from checkout.models import Transaction, PaymentMethod
from django.utils.translation import gettext as _ 
import stripe  
from paypal.standard.forms import PayPalPaymentsForm

def stripe_config(request): 
    return JsonResponse({
        'public_key': settings.STRIPE_PUBLISHABLE_KEY,
    })



def stripe_transaction(request): 
    transaction = make_transaction(request, PaymentMethod.Stripe) 
    if not transaction: 
        return JsonResponse({
            'message': _('Please enter valid information') 
        }, status=400)
    stripe.api_key= settings.STRIPE_SECRETE_KEY
    intent = stripe.PaymentIntent.create(
        amount=transaction.amount * 100, 
        currency = settings.CURRENCY, 
        payment_method_types =['card'],
        metadata={
            'transaction': transaction.id 
        }
    )
    return JsonResponse({
        'client_secret': intent['client_secret'] 
    })
    


def paypal_transaction(request): 
    transaction = make_transaction(request, PaymentMethod.Paypal)
    if not transaction: 
        return JsonResponse({
            'message': _('Please enter valid information'),
        },status=400)
    form = MyPayPalPaymentsForm(initial={
        'business': settings.PAYPAL_EMAIL, 
        'amount': transaction.amount, 
        'invoice': transaction.id, 
        'currency_code': settings.CURRENCY, 
        'return_url': f'http://{request.get_host()}{reverse("store.checkout_complete")}', 
        'cancel_url': f'http://{request.get_host()}{reverse("store.checkout")}',
        'notify_url': f'http://{request.get_host()}{reverse("checkout.paypal-webhook")}', 
    })

    return HttpResponse(form.render()) 


def make_transaction(request, pm ): 
    form = UserInfoFrom(request.POST) 
    if form.is_valid(): 
        cart = Cart.objects.filter(session=request.session.session_key).last()
        products = Product.objects.filter(pk__in=cart.item) 
            
        total = 0 
        for item in products: 
            total += item.price 
        if total <= 0: 
            return None 
        return Transaction.objects.create(
            customer = form.cleaned_data, 
            session = request.session.session_key, 
            paymentmethod= pm,
            items=cart.item, 
            amount = math.ceil(total) 
    )
        
# def send_order_email(order, products): 
#     msg_html= render_to_string('emails/order.html',{
#         'order': order, 
#         'products': products,
#     })
#     send_mail(
#         subject='New order', 
#         html_message= msg_html, 
#         message=msg_html, 
#         from_email='noreplay@example.com',
#         recipient_list=[order.customer['email']], 
#     )



# def make_order(request): 
#     if request.method != 'POST': 
#         return redirect('store.cart') 
    
#     form = UserInfoFrom(request.POST) 
#     if form.is_valid(): 
#         cart = Cart.objects.filter(session=request.session.session_key).last() 
#         products = Product.objects.filter(pk__in = cart.item)        
#         total = 0 

#         for item in products: 
#             total += item.price 

#         if total <= 0: 
#             return redirect('store.checkout') 
        
#         order = Order.objects.create(customer=form.cleaned_data, total=total)
#         for product in products: 
#             order.orderproduct_set.create(product_id=product.id, price=product.price) 
#         send_order_email(order, products)  
#         cart.delete() 
#         return redirect('store.checkout_complete') 
#     else: 
#         return redirect('store.checkout') 