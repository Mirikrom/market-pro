from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('product/', views.add_product, name='add_product'),
    path('product/<int:product_id>/', views.add_product, name='add_product_with_id'),
    path('add-unit/', views.add_unit, name='add_unit'),
    path('process-sale/', views.process_sale, name='process_sale'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
]
