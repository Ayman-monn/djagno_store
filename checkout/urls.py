from django.urls import path
from checkout import views, webhooks
from paypal.standard.ipn.views import ipn 


urlpatterns = [
    path('stripe/config', views.stripe_config, name='checkout.stripe.config') ,
    path('stripe/webhook', webhooks.stripe_webhooks,) ,
    path('stripe', views.stripe_transaction, name='checkout.stripe') ,
    path('paypal', views.paypal_transaction, name='checkout.paypal'),
    path('paypal/webhook', ipn, name='checkout.paypal-webhook'),
    ]
