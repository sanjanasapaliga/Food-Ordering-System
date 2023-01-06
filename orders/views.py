from django.shortcuts import render,redirect,HttpResponse 
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order,Payment,OrderedFood
import simplejson as json
from django.http import JsonResponse
from .utils import generate_order_number
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
import razorpay 
from FoodOrderingSystem.settings import RZP_KEY_ID,RZP_KEY_SECRET
# Create your views here.


client=razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))

@login_required(login_url='login')
def place_order(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('marketplace')
    subtotal= get_cart_amounts(request)['subtotal']
    print('subtotal'+str(subtotal))
    total_tax= get_cart_amounts(request)['tax']
    grand_total= get_cart_amounts(request)['grand_total']
    tax_data= get_cart_amounts(request)['tax_dict']
    
    if request.method=='POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.pin_code = form.cleaned_data['pin_code']
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            # order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save() # order id/ pk is generated
            order.order_number = generate_order_number(order.id)
            # order.restaurants.add(*restaurants_ids)
            order.save()
            # RazorPay Payment
            DATA = {
                "amount": float(order.total) * 100,
                "currency": "INR",
                "receipt": "receipt #"+order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            rzp_order = client.order.create(data=DATA)
            rzp_order_id = rzp_order['id']
            context={
                'order':order,
                'cart_items':cart_items,
                'subtotal':subtotal,
                'tax_dict':tax_data,
                'rzp_order_id':rzp_order_id,
                'RZP_KEY_ID':RZP_KEY_ID,
                'rzp_amount': float(order.total) * 100,
                
            }
            return render(request,'orders/place_order.html',context)
            
        else:
            print("Not Saved")
    else:
        print("Not post")
    return render(request,'orders/place_order.html',)


@login_required(login_url='login')
def payments(request):
    # Checking if the request is ajax or not
    if request.headers.get('x-requested-with')=='XMLHttpRequest' and request.method=='POST':
        # Store the details in payment model
        order_number=request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        
        order=Order.objects.get(user=request.user,order_number=order_number)
        payment=Payment(
            user = request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        payment.save()
        # update order model 
        order.payment=payment
        order.is_ordered=True
        order.save()
        # move cart items to ordered food items 
        cart_items=Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food=OrderedFood()
            ordered_food.order = order
            ordered_food.payment =payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity =item.quantity
            ordered_food.price = item.fooditem.price
            # ordered_food.amount = item.fooditem * item.quantity
            ordered_food.amount = ordered_food.quantity*ordered_food.price
            ordered_food.save()
            
        mail_subject = 'Thank you for ordering with us.'
        mail_template = 'orders/order_confirmation_email.html'

        ordered_food = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        for item in ordered_food:
            customer_subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
            'ordered_food': ordered_food,
            # 'domain': get_current_site(request),
            'customer_subtotal': customer_subtotal,
            'tax_data': tax_data,
        }
        send_notification(mail_subject, mail_template, context)
        
        # SEND ORDER RECEIVED EMAIL TO THE VENDOR
        mail_subject = 'You have received a new order.'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        for i in cart_items:
            if i.fooditem.restaurant.user.email not in to_emails:
                to_emails.append(i.fooditem.restaurant.user.email)

                ordered_food_to_restaurant = OrderedFood.objects.filter(order=order, fooditem__restaurant=i.fooditem.restaurant)


        
                context = {
                    'order': order,
                    'to_email': i.fooditem.restaurant.user.email,
                    'ordered_food_to_restaurant': ordered_food_to_restaurant,
                    # 'restaurant_subtotal': order_total_by_restaurant(order, i.fooditem.restaurant.id)['subtotal'],
                    # 'tax_data': order_total_by_restaurant(order, i.fooditem.restaurant.id)['tax_dict'],
                    # 'restaurant_grand_total': order_total_by_restaurant(order, i.fooditem.restaurant.id)['grand_total'],
                }
                send_notification(mail_subject, mail_template, context)
                # Clearing item when paument is successful
                cart_items.delete()
                response={
                    'order_number':order_number,
                    'transaction_id':transaction_id,
                }
                
                return JsonResponse(response)

    
  
    return HttpResponse('payments view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        print(tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/orders_complete.html', context)
    except:
        return redirect('home')
   