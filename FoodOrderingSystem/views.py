from django.shortcuts import render
from django.http import HttpResponse
from restaurant.models import Restaurant
def home(request):
    restaurants=Restaurant.objects.filter(is_approved=True,user__is_active=True)[:5]
    context={
        'restaurants':restaurants,
    }
    return render(request,'home.html',context)