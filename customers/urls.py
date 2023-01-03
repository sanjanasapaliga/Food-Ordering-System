from django.urls import path
import accounts.views as AccountsView
from . import views

urlpatterns = [
    path('',AccountsView.custDashboard,name='customer'),
    path('profile/',views.cprofile,name='cprofile'),
    
]
