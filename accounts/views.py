from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import UserForm
from restaurant.forms import RestaurantForm
from .models import User,UserProfile
from django.contrib import messages
# Create your views here.
def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Create the user using the form
            # password = form.cleaned_data['password']
            # user = form.save(commit=False)
            # user.set_password(password)
            # user.role = User.CUSTOMER
            # user.save()

            # Create the user using create_user method
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.customer
            user.save()

            # Send verification email
            # mail_subject = 'Please activate your account'
            # email_template = 'accounts/emails/account_verification_email.html'
            # send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')

        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()

    context={
        'form':form,
    }
    return render(request,'accounts/registerUser.html',context)

def registerRestaurant(request):
    # if request.user.is_authenticated:
        # messages.warning(request, 'You are already logged in!')
        # return redirect('myAccount')
    if request.method == 'POST':
        # store the data and create the user
        form = UserForm(request.POST)
        r_form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid() and r_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.restaurant
            user.save()
            restaurant=r_form.save(commit=False)
            restaurant.user=user
            user_profile=UserProfile.objects.get(user=user)
            restaurant.user_profile=user_profile
            restaurant.save()
            messages.success(request, 'Your account has been registered sucessfully! please wait for Verification')
            return redirect('registerRestaurant')

        else :
            print("Error")
            print(form.errors)
    else :
        form=UserForm()
        r_form=RestaurantForm()
        
    context = {
        'form': form,
        'r_form': r_form,
    }

    return render(request, 'accounts/registerRestaurant.html', context)
        # if form.is_valid() and v_form.is_valid:
        #     first_name = form.cleaned_data['first_name']
        #    
        #     user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
        #     user.role = User.VENDOR
        #     user.save()
        #     vendor = v_form.save(commit=False)
        #     vendor.user = user
        #     vendor_name = v_form.cleaned_data['vendor_name']
        #     vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
        #     user_profile = UserProfile.objects.get(user=user)
        #     vendor.user_profile = user_profile
        #     vendor.save()

            # Send verification email
            # mail_subject = 'Please activate your account'
            # email_template = 'accounts/emails/account_verification_email.html'
            # send_verification_email(request, user, mail_subject, email_template)

            # messages.success(request, 'Your account has been registered sucessfully! Please wait for the approval.')
            # return redirect('registerVendor')
    #     else:
    #         print('invalid form')
    #         print(form.errors)
    # else:
    #     form = UserForm()
    #     v_form = VendorForm()

    