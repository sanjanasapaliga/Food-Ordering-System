from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserProfile
from .context_processors import get_cart_counter, get_cart_amounts
from menu.models import Category, FoodItem

from restaurant.models import  Restaurant ,OpeningHour
from django.db.models import Prefetch
from .models import Cart 
from django.contrib.auth.decorators import login_required
# from django.db.models import Q

# from django.contrib.gis.geos import GEOSGeometry
# from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
# from django.contrib.gis.db.models.functions import Distance

from datetime import date, datetime
from orders.forms import OrderForm


def marketplace(request):
    restaurants = Restaurant.objects.filter(is_approved=True, user__is_active=True)
    restaurant_count = restaurants.count()
    context = {
        'restaurants': restaurants,
        'restaurant_count': restaurant_count,
    }
    return render(request, 'marketplace/listings.html', context)


def restaurant_detail(request, restaurant_slug):
    restaurant = get_object_or_404(Restaurant, restaurant_slug=restaurant_slug)

    categories = Category.objects.filter(restaurant=restaurant).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hours = OpeningHour.objects.filter(restaurant=restaurant).order_by('day', '-from_hour')
    
#     # Check current day's opening hours.
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_opening_hours = OpeningHour.objects.filter(restaurant=restaurant, day=today)
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'restaurant': restaurant,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/restaurant_detail.html',context)


def add_to_cart(request, food_id):
    
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    return JsonResponse({'status': 'login_required', 'message': 'Please Login to continue'})
  
    


def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if chkCart.quantity > 1:
                        # decrease the cart quantity
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/cart.html', context)


def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                # Check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                print(cart_item)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success', 'message': 'Cart item has been deleted!', 'cart_counter': get_cart_counter(request), 'cart_amount': get_cart_amounts(request)})
            except :
                return JsonResponse({'status': 'Failed', 'message': 'Cart Item does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})


def search(request):
    return HttpResponse('search')
#     if not 'address' in request.GET:
#         return redirect('marketplace')
#     else:
#         address = request.GET['address']
#         latitude = request.GET['lat']
#         longitude = request.GET['lng']
#         radius = request.GET['radius']
#         keyword = request.GET['keyword']

#         # get restaurant ids that has the food item the user is looking for
#         fetch_restaurants_by_fooditems = FoodItem.objects.filter(food_title__icontains=keyword, is_available=True).values_list('restaurant', flat=True)
        
#         restaurants = Restaurant.objects.filter(Q(id__in=fetch_restaurants_by_fooditems) | Q(restaurant_name__icontains=keyword, is_approved=True, user__is_active=True))
#         if latitude and longitude and radius:
#             pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

#             restaurants = Restaurant.objects.filter(Q(id__in=fetch_restaurants_by_fooditems) | Q(restaurant_name__icontains=keyword, is_approved=True, user__is_active=True),
#             user_profile__location__distance_lte=(pnt, D(km=radius))
#             ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

#             for v in restaurants:
#                 v.kms = round(v.distance.km, 1)
#         restaurant_count = restaurants.count()
#         context = {
#             'restaurants': restaurants,
#             'restaurant_count': restaurant_count,
#             'source_location': address,
#         }


#         return render(request, 'marketplace/listings.html', context)


@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)