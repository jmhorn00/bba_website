from django.urls import path

from . import views

app_name = 'calculators'

urlpatterns = [
    path('', views.calculator_index, name='calculator_index'),
    path('<slug:slug>/', views.calculator_detail, name='calculator_detail'),
    path('<slug:slug>/calculate/', views.calculator_submit, name='calculator_submit'),
]
