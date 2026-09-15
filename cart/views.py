from decimal import Decimal
import hashlib
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
import razorpay
from product.models import *
from .models import Cart, Payment,Wishlist, OrderPlaced,OrderProduct
from django.db.models import Q,F,Count
from address.models import Address
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.utils import timezone
import uuid
from coupon.models import Coupon,CouponUsage
from wallet.models import Wallet,WalletTransaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from address.forms import CustomerAddressForm
import logging
logger = logging.getLogger(__name__)
# Create your views here.

@login_required
def cart(request):
    user=request.user
    cart=Cart.objects.filter(user=user)
    count=cart.count()
    amount=sum(item.subtotal() for item in cart)
    total=amount+ 0 #shipping charge
    
    context={'cart':cart,
             'total':total,
             'amount':amount,
             'count':count
             }
    print('Cart:', list(cart.values('product__uid', 'quantity')))  # Debug
    print('Amount:', amount, 'Total:', total)  # Debug
    return render(request,'cart/cart.html',context)

@login_required
def add_cart(request):
    user=request.user
    print(user)
    product_id=request.GET.get('prod_uid')
    product=Product.objects.get(uid=product_id)
    cart_exist=Cart.objects.filter(user=user, product=product).first()
    if cart_exist and cart_exist.quantity >= 5:
            messages.error(request, f"Cannot add more than 5 units of {product.product_name} to cart.")
            return redirect('cart')
    if cart_exist:
        Cart.objects.filter(user=user, product=product).update(
                    quantity=F("quantity") + 1)
    else:
        Cart(user=user,product=product).save()
    messages.success(request,f"{product.product_name} added to cart.")
    return redirect('cart')

@login_required
def pluscart(request):
    if request.method =='GET':
        prod_id=request.GET['prod_id']
        try:
            cartData=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            if cartData.quantity >=5:
                return JsonResponse({'error':'Cannot add more than 5 units.'})
            cartData.quantity+=1
            cartData.save()
            user=request.user
            cart=Cart.objects.filter(user=user)
            amount=sum(item.subtotal() for item in cart)
            total=amount+ 0 #shipping charge
            subtotals=[
                {
                    'product_name':item.product.product_name,
                    'quantity':item.quantity,
                    'subtotal':item.subtotal()
                } for item in cart
            ]
            data={
                
                'quantity':cartData.quantity,
                'total':total,
                'amount':amount,
                'subtotals':subtotals,
                'count':cart.count() 
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error':'Cart item not found.'},status=400)
    
@login_required
def minuscart(request):
    if request.method =='GET':
        prod_id=request.GET['prod_id']
        try: 
            cart_data=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            if cart_data.quantity >1:
                cart_data.quantity-=1
                cart_data.save()
            else:
                cart_data.delete()
                cart_data.quantity = 0
        
            user=request.user
            cart=Cart.objects.filter(user=user)
            amount=sum(item.subtotal() for item in cart)
            total=amount+ 0 #shipping charge
            subtotals=[
                {
                    'product_name':item.product.product_name,
                    'quantity':item.quantity,
                    'subtotal':item.subtotal()
                }for item in cart
            ]
            data={
                'quantity':cart_data.quantity,
                'total':total,
                'amount':amount,
                'subtotals':subtotals,
                'count':cart.count()
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error':'Cart item not found.'},status=400)
            
    
def removecart(request):
    if request.method =='GET':
        prod_id=request.GET['prod_id']
        try:  
            cartData=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            product_name=cartData.product.product_name            
            cartData.delete()
            user=request.user
            cart=Cart.objects.filter(user=user)
            amount=sum(item.subtotal() for item in cart)
            total=amount+ 0 #shipping charge
            subtotals=[
                {
                    'product_name':item.product.product_name,
                    'quantity':item.quantity,
                    'subtotal':item.subtotal()
                } for item in cart
            ]
            data={
                
                'total':total,
                'amount':amount,
                'subtotals':subtotals,
                'count':cart.count(),
                'message':f'{product_name} removed from cart.'
            }
            return JsonResponse(data)
        except Cart.DoesNotExist:
            return JsonResponse({'error':'Cart item not found.'},status=400)
            
# Wishlist 
def wishlist(request):
    user=request.user
    wishlist=Wishlist.objects.filter(user=user)
    context={
        'wishlist':wishlist
    }
    return render(request,'cart/wishlist.html',context)

def plus_wishlist(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        print(prod_id)
        product=Product.objects.get(uid=prod_id)
        user=request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully',
        }
        return JsonResponse(data)
    
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        try:          
            product=Product.objects.get(uid=prod_id)
            user=request.user
            Wishlist.objects.filter(user=user,product=product).delete()
            return JsonResponse({'message':'Wishlist Remove Successfully'})
        
        except Product.DoesNotExist:
            return JsonResponse({'error':'Product not found'},status=400)
 
    
# Checkout page   
@login_required
def checkout_page(request):
    user = request.user
    adr = Address.objects.filter(user=user)
    cart = Cart.objects.filter(user=user)
    
    # Calculate cart total
    amount = sum(i.subtotal() for i in cart)
    totalAmount = amount  # Shipping charge is 0
    print('real total amount =', totalAmount)
    
    # Generate cart hash to detect changes
    cart_items = sorted([(str(c.product.uid), c.quantity) for c in cart], key=lambda x: x[0])
    cart_hash = hashlib.md5(json.dumps(cart_items, sort_keys=True).encode()).hexdigest()
    session_cart_hash = request.session.get('cart_hash')
    
    # Clear coupon if cart has changed
    if session_cart_hash and session_cart_hash != cart_hash:
        request.session.pop('applied_coupon_code', None)
        request.session.pop('discounted_total', None)
        request.session.pop('discount_amount', None)
    request.session['cart_hash'] = cart_hash
    
    # Get wallet balance
    try:
        wallet_user = Wallet.objects.get(user=user)
        wallet_balance = wallet_user.balance
    except Wallet.DoesNotExist:
        wallet_user = Wallet.objects.create(user=user)
        wallet_balance = 0
    
    # Apply coupon from session
    applied_coupon_code = request.session.get('applied_coupon_code')
    coupon = None
    discount_amount = 0
    if applied_coupon_code:
        try:
            coupon = Coupon.objects.get(code=applied_coupon_code, is_active=True)
            # Minimal re-validation
            if coupon.valid_from <= timezone.now() <= coupon.valid_to:
                if not coupon.min_purchase_amount or amount >= coupon.min_purchase_amount:
                    if amount - float(coupon.discount_amount) >= (0.5 * amount):
                        discount_amount = float(coupon.discount_amount)
                        totalAmount = amount - discount_amount
                    else:
                        messages.error(request, 'Coupon discount exceeds 50% of total.')
                        request.session.pop('applied_coupon_code', None)
                        request.session.pop('discounted_total', None)
                        request.session.pop('discount_amount', None)
                        totalAmount = amount
                else:
                    messages.error(request, f'Total must be at least ₹{coupon.min_purchase_amount} for this coupon.')
                    request.session.pop('applied_coupon_code', None)
                    request.session.pop('discounted_total', None)
                    request.session.pop('discount_amount', None)
                    totalAmount = amount
            else:
                messages.error(request, 'Coupon has expired.')
                request.session.pop('applied_coupon_code', None)
                request.session.pop('discounted_total', None)
                request.session.pop('discount_amount', None)
                totalAmount = amount
        except Coupon.DoesNotExist:
            messages.error(request, 'Coupon is no longer available.')
            request.session.pop('applied_coupon_code', None)
            request.session.pop('discounted_total', None)
            request.session.pop('discount_amount', None)
            totalAmount = amount
    
    request.session['total_amount'] = totalAmount
    request.session['original_amount'] = amount
    request.session['discount_amount'] = discount_amount
    
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_page')
    
    if request.method == 'POST':
        address_id = request.POST.get('custid')
        payment_mode = request.POST.get('payment')
        final_amount = request.POST.get('amount')
        print('final amount to pay =', final_amount)
        
        if not address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect('checkout')
        
        if not payment_mode:
            messages.error(request, "Please select a payment method.")
            return redirect('checkout')
        
        try:
            final_amount = float(final_amount)
            # Validate final_amount
            expected_amount = totalAmount
            if abs(final_amount - expected_amount) > 0.01:
                messages.error(request, "Invalid amount submitted.")
                return redirect('checkout')
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount format.")
            return redirect('checkout')
        
        try:
            address = Address.objects.get(uid=address_id, user=user)
        except Address.DoesNotExist:
            messages.error(request, "Invalid address selected.")
            return redirect('checkout')
        
        # Re-validate single-use coupon for order placement
        if applied_coupon_code:
            try:
                coupon = Coupon.objects.get(code=applied_coupon_code, is_active=True)
                if coupon.coupon_type == 'single-use' and CouponUsage.objects.filter(user=user, coupon=coupon).exists():
                    messages.error(request, 'Coupon already used.')
                    return redirect('checkout')
            except Coupon.DoesNotExist:
                messages.error(request, 'Coupon is no longer available.')
                return redirect('checkout')
        
        try:
            if payment_mode == 'RAZORPAY':
                razoramount = int(totalAmount * 100)
                client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
                data = {
                    "amount": razoramount,
                    "currency": "INR",
                    "receipt": f"order_rcptid_{user.id}",
                    "payment_capture": 1
                }
                try:
                    payment_response = client.order.create(data=data)
                    print(f"Razorpay order created: {payment_response}")
                    
                    order_id = payment_response['id']
                    order_status = payment_response['status']
                    
                    if order_status == 'created':
                        payment = Payment(
                            user=user,
                            amount=final_amount,
                            order_id=order_id,
                            payment_status=order_status,
                            payment_method='razorpay'
                        )
                        payment.save()
                        
                        return JsonResponse({
                            'success': True,
                            'payment_response': {
                                'id': payment_response['id'],
                                'amount': payment_response['amount']
                            },
                            'razorpay_merchant_key': settings.RAZOR_KEY_ID
                        })
                except Exception as e:
                    print(f"Razorpay error: {str(e)}")
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
            elif payment_mode == 'COD':
                order_id = str(uuid.uuid4())
                payment = Payment(
                    user=user,
                    amount=final_amount,
                    order_id=order_id,
                    payment_id=order_id,
                    payment_status='pending',
                    payment_method='COD'
                )
                payment.save()
                
                order = OrderPlaced.objects.create(
                    user=user,
                    address=address,
                    payment=payment
                )
                
                for c in cart:
                    OrderProduct(
                        orders=order,
                        product=c.product,
                        quantity=c.quantity,
                        order_amount=c.product.get_selling_price()
                    ).save()
                    c.delete()
                
                if coupon:
                    CouponUsage.objects.create(user=user, coupon=coupon)
                    request.session.pop('applied_coupon_code', None)
                    request.session.pop('discounted_total', None)
                    request.session.pop('discount_amount', None)
                
                messages.success(request, "Order placed successfully!")
                return JsonResponse({'success': True, 'redirect_url': '/order_list/'})
            
            elif payment_mode == 'wallet':
                if wallet_balance < final_amount:
                    messages.error(request, 'Insufficient wallet balance.')
                    return JsonResponse({'success': False, 'error': 'Insufficient wallet balance'}, status=400)
                
                order_id = str(uuid.uuid4())
                payment = Payment(
                    user=user,
                    amount=final_amount,
                    order_id=order_id,
                    payment_id=order_id,
                    payment_status='success',
                    payment_method='wallet',
                    paid=True
                )
                payment.save()
                
                order = OrderPlaced.objects.create(
                    user=user,
                    address=address,
                    payment=payment
                )
                
                for c in cart:
                    OrderProduct(
                        orders=order,
                        product=c.product,
                        quantity=c.quantity,
                        order_amount=c.product.get_selling_price()
                    ).save()
                    c.delete()
                
                if coupon:
                    CouponUsage.objects.create(user=user, coupon=coupon)
                    request.session.pop('applied_coupon_code', None)
                    request.session.pop('discounted_total', None)
                    request.session.pop('discount_amount', None)
                
                wallet_user.balance -= final_amount
                wallet_user.save()
                
                WalletTransaction.objects.create(
                    wallet=wallet_user,
                    transaction_type='DEBIT',
                    amount=final_amount,
                    description=f"Payment for order {order_id}",
                    payment_id=order_id
                )
                
                messages.success(request, "Order placed successfully!")
                return JsonResponse({'success': True, 'redirect_url': '/order_list/'})
                
        except Exception as e:
            print(f"Order processing error: {str(e)}")
            messages.error(request, f'Error processing order: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    context = {
        'address': adr,
        'cart_item': cart,
        'total': totalAmount,
        'original_total': amount,
        'discount_amount': discount_amount,
        'wallet_balance': wallet_balance,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'applied_coupon_code': applied_coupon_code
    }
    return render(request, 'cart/checkout.html', context)

@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        
        # Get payment details from POST data
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        
        # Verify payment signature
        params_dict = {
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            
            # Update payment status
            payment = Payment.objects.get(order_id=order_id)
            payment.payment_id = payment_id
            payment.payment_status = 'success'
            payment.paid=True
            payment.save()
            
            # Create order and order products
            user = request.user
            address = Address.objects.get(uid=request.POST.get('address_id'))
            
            order = OrderPlaced.objects.create(
                user=user,
                address=address,
                payment=payment
            )
            
            # Process cart items
            cart = Cart.objects.filter(user=user)
            for item in cart:
                OrderProduct.objects.create(
                    orders=order,
                    product=item.product,
                    quantity=item.quantity,
                    order_amount=item.product.get_selling_price()
                )
                item.delete()
            applied_coupon_code=request.session.get('applied_coupon_code')
            if applied_coupon_code:
                try:
                    coupon=Coupon.objects.get(code=applied_coupon_code,is_active=True)       
                    CouponUsage.objects.create(user=user,coupon=coupon)
                    request.session.pop('applied_coupon_code', None)
                    request.session.pop('discounted_total', None)
                    request.session.pop('discount_amount', None)
                except Coupon.DoesNotExist:
                    pass
            return redirect('order_list')
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Payment verification failed'}, status=400)
        
@csrf_exempt  
def apply_coupon(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        user = request.user
        print("Coupon Code received:", code)
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            original_amount = request.session.get('original_amount', 0)
            if not original_amount:
                return JsonResponse({'error': 'Cart is empty or total not found'}, status=400)
            
            # Validate coupon
            if not (coupon.valid_from <= timezone.now() <= coupon.valid_to):
                return JsonResponse({'error': 'Coupon has expired'}, status=400)
            
            if coupon.coupon_type == 'single-use' and CouponUsage.objects.filter(user=user, coupon=coupon).exists():
                return JsonResponse({'error': 'Coupon already used'}, status=400)
            
            if coupon.min_purchase_amount and original_amount < coupon.min_purchase_amount:
                return JsonResponse({'error': f'Total amount must be at least ₹{coupon.min_purchase_amount} to use this coupon.'}, status=400)
            
            # Calculate discount
            discount_amount = float(coupon.discount_amount)
            final_total = original_amount - discount_amount
            
            if final_total < (0.5 * original_amount):
                return JsonResponse({'error': 'After applying this coupon, total should be above 50% of original amount.'}, status=400)
            
            # Store in session
            request.session['discounted_total'] = final_total
            request.session['applied_coupon_code'] = code
            request.session['discount_amount'] = discount_amount
            
            print("Discount applied successfully:", discount_amount)
            
            return JsonResponse({
                'success': True,
                'discount_amount': discount_amount,
                'final_total': final_total
            })
        except Coupon.DoesNotExist:
            return JsonResponse({'error': 'Invalid coupon code'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
        
@csrf_exempt
def remove_coupon(request):
    if request.method == 'POST':
        original_amount = request.session.get('original_amount', 0)
        request.session.pop('discounted_total', None)
        request.session.pop('applied_coupon_code', None)
        request.session.pop('discount_amount', None)
        return JsonResponse({
            'success': True,
            'final_total': original_amount
        })
    return JsonResponse({'error': 'No coupon to remove'}, status=400)
   
@login_required        
def add_address(request):
    
    if request.method=='POST':
        try:
            logger.debug(f"POST data: {request.POST}")
            form=CustomerAddressForm(request.POST)
            if form.is_valid():
                if Address.objects.filter(
                    user=request.user,
                    name=form.cleaned_data['name'],
                    mobile=form.cleaned_data['mobile'],
                    locality=form.cleaned_data['locality'],
                    city=form.cleaned_data['city'],
                    state=form.cleaned_data['state'],
                    zip_code=form.cleaned_data['zip_code'],
                    type=form.cleaned_data['type']
                ).exists():
                    return JsonResponse({'success':False,'error':'This address exists'},status=400)
                
                address = form.save(commit=False)
                address.user=request.user
                address.save()
                print(address)
                logger.info(f"Address added for user {request.user.username}: {address.uid}")
                return JsonResponse({
                    'success':True,
                    'address':{
                        'uid':str(address.uid),
                        'name':address.name,
                        'mobile':address.mobile,
                        'locality':address.locality,
                        'city':address.city,
                        'state':address.state,
                        'zip_code':address.zip_code,
                        'type': address.type,
                    }
                })
            else:
                logger.warning(f"Form validation failed: {form.errors}")
                return JsonResponse({'success':False, 'errors': form.errors},status=400)
        except Exception as e:
            logger.error(f"Error adding address for user {request.user.username}: {str(e)}")
            return JsonResponse({'success':False,'error':f'Server error: {str(e)}'},status=500)
    logger.warning(f"Invalid request method for add_address: {request.method}")
    return JsonResponse({'success':False,'errors':'Invalid request'},status=400)


# class checkout(View):
#     def get(self,request):
#         user=request.user
#         adr=Address.objects.filter(user=user)
#         cart=Cart.objects.filter(user=user)
#         amount=0
#         for i in cart:
#             value=i.quantity*i.product.discount
#             amount+=value
#         totalAmount=amount+ 0 #shipping charge
#         razoramount=int(totalAmount * 100)
#         print(totalAmount,"amount in paisa",razoramount)
        
#         client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
#         data = { "amount": razoramount, "currency": "INR", "receipt": "order_rcptid_11","payment_capture": "1" }
#         payment_response = client.order.create(data=data)
#         print(payment_response)
        
#         order_id=payment_response['id']
#         order_status=payment_response['status']
#         if order_status=='created':
#             payment=Payment(
#                 user=user,
#                 amount=totalAmount,
#                 razorpay_order_id=order_id,
#                 razorpay_payment_status=order_status
#             )
#             payment.save()      
        
#         context={'address':adr,
#                  'cart_item':cart,
#                  'total':totalAmount,
#                  'data':data,
#                  'payment_response':payment_response,
#                  'order_id':order_id,
#                  'order_status':order_status
#                  }
#         return render(request,'cart/checkout.html',context)

# @require_POST
# @csrf_protect
# def save_address(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         phone = request.POST.get('phone')
#         address_type = request.POST.get('address_type')  
#         locality = request.POST.get('locality')
#         city = request.POST.get('city')
#         state = request.POST.get('state')
#         zip = request.POST.get('zip')

#         # Create a new address
#         print(name,phone,address_type)

#         return JsonResponse({'status': 'success', 'message': 'Address added successfully'})
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
# def payment_done(request):
#     order_id=request.GET.get('order_id')
#     payment_id=request.GET.get('payment_id')
#     cust_id=request.GET.get('cust_id')
    
#     user=request.user
#     customer=Address.objects.get(id=cust_id)
    
#     #To update payment status and payment id
#     payment=Payment.objects.get(razorpay_order_id=order_id)
#     payment.paid= True
#     payment.razorpay_payment_id=payment_id
#     payment.save()
    
#     #To save order details
#     cart=Cart.objects.filter(user=user)
#     for c in cart:
#         OrderPlaced(user=user,address=customer,product=c.product,quantity=c.quantity,payment=payment).save()
#         c.delete()
#     return redirect("orders")

@login_required
def order_list(request):
    user=request.user
    order_data=OrderPlaced.objects.filter(user=user).select_related('address', 'payment').prefetch_related('orderproduct_set__product')
    context={
        'orders':order_data
    }
    return render(request,'cart/order_list.html',context)

@login_required
def order_cancel(request,pk):
    product=OrderProduct.objects.get(pk=pk)
    if not product.is_cancellable():
        messages.error(request,"This order cannot be canceled as it is past the 7-days canceelation period")
        return redirect('order_list')
    if product.status == 'delivered':
        messages.error(request,'Delivered orders cannot bo canceled.')
        return redirect('order_list')
    
    order=product.orders
    payment= order.payment
    
    refund_applicable = payment.payment_method.lower() in ['razorpay','wallet']
    
    product.status='canceled'
    product.quantity=0
    
    product_amount=Decimal(str(product.order_amount))
    payment.amount-=float(product_amount)
    payment.save()
    if refund_applicable:      
        wallet=order.user.wallet
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='REFUND',
            amount=product_amount,
            description=f"Refund for oder {payment.order_id}",
            payment_id=payment.payment_id
        )
        wallet.balance += product_amount
        wallet.save()
    
    product.save()
    if refund_applicable:
        messages.success(request, f"Order canceled succesfully. Refund of ₹{product_amount} crdited to your wallet.")
    else:
        messages.success(request, "Order canceled succefully.No refund processed as payment was via COD.")
    return redirect('order_list')

