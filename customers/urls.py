from django.urls import path
import accounts.views as AccountsView
from . import views

urlpatterns = [
    path('',AccountsView.custDashboard,name='customer'),
    path('profile/',views.cprofile,name='cprofile'),
    path('my_orders/',views.my_orders,name='customer_my_orders'),
    path('order_details/<int:order_number>/',views.order_detail,name='order_detail')
    
]
