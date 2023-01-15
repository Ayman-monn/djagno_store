from django.views.decorators.csrf import csrf_exempt
import django_store.settings as settings 
from django.http import HttpResponse 
from checkout.models import Transaction 
from store.models import Product, Order
from checkout import models  
from django.core.mail import send_mail
from django.template.loader import render_to_string
import stripe 
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received 

@csrf_exempt 
def stripe_webhooks(request):
    print('Stripe Webhook') 
    event = None
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print('Invalid Payload')
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Invalid signature')
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        print('payment_intent.succeeded')
        transaction_id = payment_intent.metadata.transaction
        make_order(transaction_id) 
    #   print(payment_intent.metadata)
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return HttpResponse(status=200)

@csrf_exempt 
def paypal_webhook(sender, **kwargs): 
    if sender.payment_status == ST_PP_COMPLETED: 
        if sender.reciever_email != settings.PAYPAL_EMAIL: 
            return 
        print('PaymentIntent was successful') 
        make_order(sender.invoice) 
        
valid_ipn_received.connect(paypal_webhook) 

def make_order(transaction_id): 
    transaction = Transaction.objects.get(pk=transaction_id)
    transaction.status = models.TransactionStatus.Completed
    transaction.save() 
    order = Order.objects.create(transaction=transaction)
    products =Product.objects.filter(pk__in=transaction.items)
    for product in products:
        order.orderproduct_set.create(
            product_id=product.id,
            price = product.price, 
        )

    msg_html= render_to_string('emails/order.html',{
        'order': order, 
        'products': products,
    })
    send_mail(
        subject='New order', 
        html_message= msg_html, 
        message=msg_html, 
        from_email='noreplay@example.com',
        recipient_list=[order.transaction.customer_email], 
    )
     

