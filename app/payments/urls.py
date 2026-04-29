from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.pay, name='pay'),
    path('checkout/', views.create_checkout_session, name='create_checkout'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
