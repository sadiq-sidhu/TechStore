def checkout_page(request):
    user=request.user
    adr=Address.objects.filter(user=user)
    cart=Cart.objects.filter(user=user)
    amount = sum(i.quantity * i.product.discount for i in cart)
    totalAmount=amount+ 0 #shipping charge
    razoramount=int(totalAmount * 100)
    
    try:
        wallet_user=Wallet.objects.get(user=user)
        wallet_balance=wallet_user.balance
    except Wallet.DoesNotExist:
        wallet_user=Wallet.objects.create(user=user)
        wallet_balance=0
    request.session['total_amount'] = totalAmount
    
    print(totalAmount,"amount in paisa",razoramount)
    
    if request.method == 'POST':
        # Get the selected address from POST request
        address_id = request.POST.get('custid')
        payment_mode = request.POST.get('payment')
        final_amount = request.POST.get('amount')  # Get final amount
        print("Final Amount:", amount)
        print(address_id,"addresss iddddd")
        print("Address ID:", request.POST.get('custid'))
        print("Payment Mode:", request.POST.get('payment'))
        print("All POST data:", request.POST)
        
        address = Address.objects.get(uid=address_id)
        # Get payment mode
        print(payment_mode)
        
        # Create Order object
        if payment_mode == 'RAZORPAY':
            # Create Razorpay order   
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            data = {"amount": razoramount,
                    "currency": "INR",
                    "receipt": "order_rcptid_11",
                    "payment_capture": "1" }
            try: 
                payment_response = client.order.create(data=data)
                print(payment_response)
                
                order_id=payment_response['id']
                order_status=payment_response['status']
                
                if order_status=='created':
                    payment=Payment(
                        user    =user,
                        amount  =final_amount,
                        order_id=order_id,
                        payment_status=order_status,
                        payment_method='razorpay'
                    )
                    payment.save() 
            
                return JsonResponse({
                    'payment_response': payment_response,
                    'razorpay_merchant_key': settings.RAZOR_KEY_ID
                })
                
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
            
        # COD 
        elif payment_mode == 'cod' or payment_mode=='COD':
            order_id=str(uuid.uuid4())
            order_status='pending'
            payment=Payment(
                    user=user,
                    amount=final_amount,
                    order_id=order_id,
                    payment_id=order_id,
                    payment_status=order_status,
                    payment_method='COD'
                )
            payment.save()
            order=OrderPlaced.objects.create(
                user=user,
                address=address,
                payment=payment,
            )
            cart=Cart.objects.filter(user=user)
            for c in cart:
                OrderProduct(orders=order,
                            product=c.product,
                            quantity=c.quantity,
                            order_amount=c.product.discount
                            ).save()
                c.delete()
            return redirect('order_list')
        
        elif payment_mode=='wallet':
            
            if wallet_balance < float(amount):
                messages.error(request,'Insufficient wallet balance.')
                return redirect('order_list')
            order_id=str(uuid.uuid4())
            payment_status='success'
            payment=Payment(
                user=user,
                amount=final_amount,
                order_id=order_id,
                payment_id=order_id,
                payment_status=payment_status,
                payment_method='wallet',
                paid=True
            )
            payment.save()
            
            order=OrderPlaced.objects.create(
                user=user,
                address=address,
                payment=payment,
            )
            cart=Cart.objects.filter(user=user)
            for c in cart:
                OrderProduct(
                    orders=order,
                    product=c.product,
                    order_amount=c.product.discount
                    ).save()
                c.delete()
            wallet_user.balance=float(wallet_user.balance)-float(final_amount)
            wallet_user.save()
            
            WalletTransaction.objects.create(
                wallet=wallet_user,
                transaction_type='DEBIT',
                amount=final_amount,
                description=f"Payment for order {order_id}",
                payment_id=order_id
            )
            return redirect ('order_list')
    else:
        # Render checkout page with addresses and datas.
        context = {
            'address':adr,
            'cart_item':cart,
            'total':totalAmount,
            'wallet_balance':wallet_balance
            
        }
        return render(request, 'cart/checkout.html', context)
    
<script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
<script>
    const applyCouponUrl = "{% url 'apply_coupon' %}";  // Django resolves this URL here
    const removeCouponUrl= '{% url "remove_coupon" %}';
</script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        console.log("Script loaded");
        
        // Get important elements
        const walletRadio = document.getElementById('wallet');
        const walletBalance = parseFloat('{{ wallet_balance }}');
        const totalAmountDisplay = document.getElementById('total_amount');
        
        // Function to check wallet eligibility based on current total amount
        function checkWalletEligibility() {
            const currentTotal = parseFloat(totalAmountDisplay.textContent);
            console.log("Checking wallet eligibility. Balance:", walletBalance, "Current total:", currentTotal);
            
            if (walletBalance >= currentTotal) {
                // Enable wallet option
                walletRadio.disabled = false;
                walletRadio.parentElement.querySelector('label').style.color = '';
                
                // Remove insufficient balance message if it exists
                const errorSpan = walletRadio.parentElement.querySelector('.caption span');
                if (errorSpan) {
                    errorSpan.remove();
                }
                console.log("Wallet enabled - sufficient balance");
            } else {
                // Disable wallet option
                walletRadio.disabled = true;
                if (walletRadio.checked) {
                    walletRadio.checked = false; // Uncheck if it was selected
                }
                walletRadio.parentElement.querySelector('label').style.color = '#aaa';
                
                // Add or update insufficient balance message
                let errorSpan = walletRadio.parentElement.querySelector('.caption span');
                if (!errorSpan) {
                    errorSpan = document.createElement('span');
                    errorSpan.style.color = 'red';
                    walletRadio.parentElement.querySelector('.caption p').appendChild(document.createElement('br'));
                    walletRadio.parentElement.querySelector('.caption p').appendChild(errorSpan);
                }
                errorSpan.textContent = 'Insufficient balance for this order.';
                console.log("Wallet disabled - insufficient balance");
            }
        }
        
        // Observer to watch for changes in the total amount display
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'characterData' || mutation.type === 'childList') {
                    checkWalletEligibility();
                }
            });
        });
        
        // Start observing the total amount element
        observer.observe(totalAmountDisplay, { 
            characterData: true, 
            childList: true,
            subtree: true 
        });
        
        // Apply coupon button click handler
        document.getElementById('apply_coupon_button').addEventListener('click', function(event) {
            console.log("Apply coupon button clicked"); 
            event.preventDefault();  

            const couponCodeInput = document.getElementById('coupon_code');
            const couponCode = couponCodeInput.value;

            console.log("Coupon code:", couponCode);  
            fetch(applyCouponUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({ code: couponCode })
            })
            .then(response => {
                console.log("Received response");
                return response.json();
            })
            .then(data => {
                console.log("Response data:", data);
                const messageDiv = document.getElementById('coupon_message');
                const discountDiv = document.getElementById('discount_display');
                const totalAmountDisplay = document.getElementById('total_amount');
                const applyButton = document.getElementById('apply_coupon_button');
                const removeButton = document.getElementById('remove_coupon_button');
                const hiddenTotalAmount = document.getElementById('hidden_total_amount');

                if (data.success) {
                    messageDiv.textContent = 'Coupon applied successfully!';
                    discountDiv.textContent = `₹${data.discount_amount}`;
                    totalAmountDisplay.textContent = `${data.final_total}`;
                    hiddenTotalAmount.value = data.final_total; // Update hidden field

                    applyButton.disabled = true;
                    applyButton.style.backgroundColor = 'gray';
                    couponCodeInput.placeholder = couponCode;
                    couponCodeInput.value = '';
                    couponCodeInput.readOnly = true;

                    removeButton.style.display = 'inline-block';
                    
                    // Check wallet eligibility after coupon application
                    setTimeout(checkWalletEligibility, 100);
                } else {
                    messageDiv.textContent = data.error;
                    discountDiv.textContent = '';
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });

        // Remove coupon button click handler
        document.getElementById('remove_coupon_button').addEventListener('click', function() {
            const couponCodeInput = document.getElementById('coupon_code');
            const messageDiv = document.getElementById('coupon_message');
            const discountDiv = document.getElementById('discount_display');
            const totalAmountDisplay = document.getElementById('total_amount');
            const applyButton = document.getElementById('apply_coupon_button');
            const removeButton = document.getElementById('remove_coupon_button');
            const hiddenTotalAmount = document.getElementById('hidden_total_amount');

            // Reset the discount and message areas
            messageDiv.textContent = '';
            discountDiv.textContent = '';

            // Retrieve the original total from the data attribute
            const originalTotal = document.getElementById('total_amount_display').getAttribute('data-original-total');
            totalAmountDisplay.textContent = originalTotal;  // Reset to original total
            hiddenTotalAmount.value = originalTotal; // Reset hidden field

            // Enable the apply button and reset styles
            applyButton.disabled = false;
            applyButton.style.backgroundColor = '';  // Reset button color
            couponCodeInput.placeholder = 'Enter coupon code';  // Reset placeholder
            couponCodeInput.value = '';  // Clear input value
            couponCodeInput.readOnly = false;  // Make input editable

            // Hide the remove button
            removeButton.style.display = 'none';

            // Clear session discount on the server side
            fetch(removeCouponUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Coupon removed successfully');
                    // Check wallet eligibility after coupon removal
                    setTimeout(checkWalletEligibility, 100);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
        
        // Run on page load
        checkWalletEligibility();
    });
</script>
</script>