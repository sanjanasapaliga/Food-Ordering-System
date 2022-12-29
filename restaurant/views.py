# from unicodedata import category
# from urllib import response
# from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
# from django.db import IntegrityError

# from menu.forms import CategoryForm, FoodItemForm
# from orders.models import Order, OrderedFood
# import restaurant
from .forms import RestaurantForm #, OpeningHourForm
from accounts.forms import UserProfileForm

from accounts.models import UserProfile
from .models import  Restaurant #OpeningHour,
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_restaurant
from menu.models import Category, FoodItem
# from django.template.defaultfilters import slugify


def get_restaurant(request):
    restaurant = Restaurant.objects.get(user=request.user)
    return restaurant


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def rprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    restaurant = get_object_or_404(Restaurant, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm( request.POST, request.FILES,instance=profile)
        restaurant_form = RestaurantForm(request.POST, request.FILES,instance=restaurant)
        if profile_form.is_valid() and restaurant_form.is_valid():
            profile_form.save()
            restaurant_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('rprofile')
        else:
            print(profile_form.errors)
            print(restaurant_form.errors)
    else:
        profile_form = UserProfileForm(instance = profile)
        restaurant_form = RestaurantForm(instance=restaurant)

    context = {
        'profile_form': profile_form,
        'restaurant_form': restaurant_form,
        'profile': profile,
        'restaurant': restaurant,
    }
    return render(request, 'restaurant/rprofile.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def menu_builder(request):
    restaurant = get_restaurant(request)
    categories = Category.objects.filter(restaurant=restaurant).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'restaurant/menu_builder.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_restaurant)
def fooditems_by_category(request, pk=None):
    restaurant = get_restaurant(request)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(restaurant=restaurant, category=category)
    context = {
        'fooditems': fooditems,
        'category': category,
    }
    return render(request, 'restaurant/fooditems_by_category.html', context)


# @login_required(login_url='login')
# @user_passes_test(check_role_restaurant)
# def add_category(request):
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             category_name = form.cleaned_data['category_name']
#             category = form.save(commit=False)
#             category.restaurant = get_restaurant(request)
            
#             category.save() # here the category id will be generated
#             category.slug = slugify(category_name)+'-'+str(category.id) # chicken-15
#             category.save()
#             messages.success(request, 'Category added successfully!')
#             return redirect('menu_builder')
#         else:
#             print(form.errors)

#     else:
#         form = CategoryForm()
#     context = {
#         'form': form,
#     }
#     return render(request, 'restaurant/add_category.html', context)


# @login_required(login_url='login')
# @user_passes_test(check_role_restaurant)
# def edit_category(request, pk=None):
#     category = get_object_or_404(Category, pk=pk)
#     if request.method == 'POST':
#         form = CategoryForm(request.POST, instance=category)
#         if form.is_valid():
#             category_name = form.cleaned_data['category_name']
#             category = form.save(commit=False)
#             category.restaurant = get_restaurant(request)
#             category.slug = slugify(category_name)
#             form.save()
#             messages.success(request, 'Category updated successfully!')
#             return redirect('menu_builder')
#         else:
#             print(form.errors)

#     else:
#         form = CategoryForm(instance=category)
#     context = {
#         'form': form,
#         'category': category,
#     }
#     return render(request, 'restaurant/edit_category.html', context)


# @login_required(login_url='login')
# @user_passes_test(check_role_restaurant)
# def delete_category(request, pk=None):
#     category = get_object_or_404(Category, pk=pk)
#     category.delete()
#     messages.success(request, 'Category has been deleted successfully!')
#     return redirect('menu_builder')


# @login_required(login_url='login')
# @user_passes_test(check_role_restaurant)
# def add_food(request):
#     if request.method == 'POST':
#         form = FoodItemForm(request.POST, request.FILES)
#         if form.is_valid():
#             foodtitle = form.cleaned_data['food_title']
#             food = form.save(commit=False)
#             food.restaurant = get_restaurant(request)
#             food.slug = slugify(foodtitle)
#             form.save()
#             messages.success(request, 'Food Item added successfully!')
#             return redirect('fooditems_by_category', food.category.id)
#         else:
#             print(form.errors)
#     else:
#         form = FoodItemForm()
#         # modify this form
#         form.fields['category'].queryset = Category.objects.filter(restaurant=get_restaurant(request))
#     context = {
#         'form': form,
#     }
#     return render(request, 'restaurant/add_food.html', context)



# @login_required(login_url='login')
# @user_passes_test(check_role_restaurant)
# def edit_food(request, pk=None):
#     food = get_object_or_404(FoodItem, pk=pk)
#     if request.method == 'POST':
#         form = FoodItemForm(request.POST, request.FILES, instance=food)
#         if form.is_valid():
#             foodtitle = form.cleaned_data['food_title']
#             food = form.save(commit=False)
#             food.restaurant = get_restaurant(request)
#             food.slug = slugify(foodtitle)
#             form.save()
#             messages.success(request, 'Food Item updated successfully!')
#             return redirect('fooditems_by_category', food.category.id)
#         else:
#             print(form.errors)

#     else:
#         form = FoodItemForm(instance=food)
#         form.fields['category'].queryset = Category.objects.filter(restaurant=get_restaurant(request))
#     context = {
#         'form': form,
#         'food': food,
#     }
#     return render(request, 'restaurant/edit_food.html', context)


# @login_required(login_url='login')
# @user_passes_test(check_role_restaurant)
# def delete_food(request, pk=None):
#     food = get_object_or_404(FoodItem, pk=pk)
#     food.delete()
#     messages.success(request, 'Food Item has been deleted successfully!')
#     return redirect('fooditems_by_category', food.category.id)


# def opening_hours(request):
#     opening_hours = OpeningHour.objects.filter(restaurant=get_restaurant(request))
#     form = OpeningHourForm()
#     context = {
#         'form': form,
#         'opening_hours': opening_hours,
#     }
#     return render(request, 'restaurant/opening_hours.html', context)


# def add_opening_hours(request):
#     # handle the data and save them inside the database
#     if request.user.is_authenticated:
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
#             day = request.POST.get('day')
#             from_hour = request.POST.get('from_hour')
#             to_hour = request.POST.get('to_hour')
#             is_closed = request.POST.get('is_closed')
            
#             try:
#                 hour = OpeningHour.objects.create(restaurant=get_restaurant(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
#                 if hour:
#                     day = OpeningHour.objects.get(id=hour.id)
#                     if day.is_closed:
#                         response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
#                     else:
#                         response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
#                 return JsonResponse(response)
#             except IntegrityError as e:
#                 response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
#                 return JsonResponse(response)
#         else:
#             HttpResponse('Invalid request')


# def remove_opening_hours(request, pk=None):
#     if request.user.is_authenticated:
#         if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#             hour = get_object_or_404(OpeningHour, pk=pk)
#             hour.delete()
#             return JsonResponse({'status': 'success', 'id': pk})


# def order_detail(request, order_number):
#     try:
#         order = Order.objects.get(order_number=order_number, is_ordered=True)
#         ordered_food = OrderedFood.objects.filter(order=order, fooditem__restaurant=get_restaurant(request))

#         context = {
#             'order': order,
#             'ordered_food': ordered_food,
#             'subtotal': order.get_total_by_restaurant()['subtotal'],
#             'tax_data': order.get_total_by_restaurant()['tax_dict'],
#             'grand_total': order.get_total_by_restaurant()['grand_total'],
#         }
#     except:
#         return redirect('restaurant')
#     return render(request, 'restaurant/order_detail.html', context)


# def my_orders(request):
#     restaurant = Vendor.objects.get(user=request.user)
#     orders = Order.objects.filter(restaurants__in=[restaurant.id], is_ordered=True).order_by('created_at')

#     context = {
#         'orders': orders,
#     }
#     return render(request, 'restaurant/my_orders.html', context)
