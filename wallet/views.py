
from decimal import Decimal
import json
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
import razorpay.errors
from . models import Wallet,WalletTransaction
from . forms import walletAddMoneyForm
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
@login_required
def wallet_view(request):
    wallet,crated = Wallet.objects.get_or_create(user=request.user)#get_or_create return a tuple that why use 'wallet'and'create'
    transactions= wallet.transactions.order_by('-created_at')
    form=walletAddMoneyForm()
    context={
        'wallet':wallet,'transactions':transactions,'form':form
    }
    return render(request,'wallet/wallet.html',context)
@login_required
def add_money(request):
    if request.method == 'POST':
        form=walletAddMoneyForm(request.POST)
        if form.is_valid():
            amount = float(form.cleaned_data['amount'])
            print(amount)
            try:
                
                razorpay_order=client.order.create({
                    'amount':int(amount*100),
                    'currency':'INR',
                    'payment_capture':1,
                })
                return JsonResponse({'payment_response':razorpay_order,'razorpay_merchant_key': settings.RAZOR_KEY_ID})
            except Exception as e:
                return JsonResponse({'error':str(e)},status=500)
        
        else:
            return JsonResponse({'error':'invalid amount'},status=400)
    return JsonResponse({'error':'Invalid request method'},status=400)
@csrf_exempt
def payment_callback(request):
    if request.method=='POST':
        data= json.loads(request.body)
        razorpay_payment_id =data.get('razorpay_payment_id')
        razorpay_order_id=data.get('razorpay_order_id')
        razorpay_signature=data.get('razorpay_signature')
        
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id':razorpay_order_id,
                'razorpay_payment_id':razorpay_payment_id,
                'razorpay_signature':razorpay_signature
            })   
            payment=client.payment.fetch(razorpay_payment_id)
            if payment['status']=='captured':
                print(payment)
                print(payment['amount'])
                amount=Decimal((payment['amount'])/100)
                print(amount)
                wallet,_=Wallet.objects.get_or_create(user=request.user)
                wallet.balance += amount
                wallet.save()
                print(wallet.balance)
                transaction=WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='CREDIT',
                    description='Added money via Razorpay.',
                    payment_id=razorpay_payment_id
                )
                return JsonResponse({'success':True,'message':'Payment succesfull','new_balance':wallet.balance})     
            return JsonResponse({'success':False,'message':'Payment failed'},status=400)
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'success':False,'message':'Payment signature verification faailed.'})
    return JsonResponse({'error':'Invalid request method'},status=400)

            