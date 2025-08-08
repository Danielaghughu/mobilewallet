from django.shortcuts import render, redirect, get_object_or_404
from .models import Wallet, Transaction, TransactionType, TransactionMode,  TransactionStatus
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.http import JsonResponse
import requests
from django.utils import timezone
from django.core.mail import send_mail
import random
import string
import json
from datetime import timedelta
from django.core.cache import cache
from .paystack import initiate, verify


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            try:
                user = User.objects.create(username=username, email=email)
                user.set_password(password1)
                user.save() 
                wallet = Wallet.objects.create(user=user)
                messages.success(request, 'Account created successfully! Please login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                return redirect('signup')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'wallet/signup.html')

def callback(request):
    return render(request, 'wallet/callback.html')

@login_required
def index(request):
    paystack_secret_key = getattr(settings, 'PAYSTACK_SECRET_KEY', None)
    wallet = get_object_or_404(Wallet, user=request.user)
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')[:5]
    transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')[:5]
    return render(request, 'wallet/home.html', {'wallet': wallet, 'transactions': transactions, 'paystack_secret_key': paystack_secret_key})

def verify_account(request):
    if request.method == 'GET':
        account_number = request.GET.get('account_number')
        bank_code = request.GET.get('bank_code')

        headers = {
            'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'
        }

        url = f'https://api.paystack.co/bank/resolve?account_number={account_number}&bank_code={bank_code}'
        response = requests.get(url, headers=headers)
        return JsonResponse(response.json())

@login_required
def transfer(request):
    paystack_public_key = getattr(settings, 'PAYSTACK_PUBLIC_KEY', None)
    if request.method == 'POST':

        receiver_username = request.POST['receiver']
        amount = float(request.POST['amount'])
        sender_wallet = get_object_or_404(Wallet, user=request.user)

        try:
            receiver_user = User.objects.get(username=receiver_username)
            receiver_wallet = Wallet.objects.get(user=receiver_user)
        except User.DoesNotExist:
            messages.error(request, 'Receiver does not exist.')
            return redirect('transfer')

        if sender_wallet.balance >= amount:
            sender_wallet.balance -= amount
            receiver_wallet.balance += amount
            sender_wallet.save()
            receiver_wallet.save()

            Transaction.objects.create(wallet=sender_wallet, type='transfer', amount=-amount)
            Transaction.objects.create(wallet=receiver_wallet, type='transfer', amount=amount)
            messages.success(request, 'Transfer successful!')
        else:
            messages.error(request, 'Insufficient balance')

        return redirect('home')
    return render(request, 'wallet/transfer.html', {'paystack_public_key': paystack_public_key})

@login_required
def buy_airtime(request):
    if request.method == 'POST':
        network = request.POST['network']
        phone = request.POST['phone']
        amount = float(request.POST['amount'])
        wallet = get_object_or_404(Wallet, user=request.user)
        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            Transaction.objects.create(wallet=wallet, type=f"airtime ({network})", amount=-amount)
            messages.success(request, f"₦{amount} airtime successfully sent to {phone} on {network} network!")
        else:
            messages.error(request, 'Insufficient balance')
        return redirect('home')
    return render(request, 'wallet/buy_airtime.html')
def buy_data(request):
    if request.method == 'POST':
        network = request.POST['network']
        phone = request.POST['phone']
        plan = request.POST['plan']
        amount = float(request.POST['amount'])
        wallet = get_object_or_404(Wallet, user=request.user)
        if wallet.balance >= amount:
            wallet.balance -= amount
            wallet.save()
            Transaction.objects.create(wallet=wallet, type=f"data ({network} - {plan})", amount=-amount)
            messages.success(request, f"{plan} purchased for {phone} on {network} for ₦{amount}!")
        else:
            messages.error(request, 'Insufficient balance')
        return redirect('home')
    return render(request, 'wallet/buy_data.html')
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    return render(request, 'wallet/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

@csrf_exempt
@login_required
def fund_wallet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            user = request.user
            if not user:
                return JsonResponse({'error': 'User is not authenticated.'}, status=401)

            amount = data.get('amount')
            if not amount:
                return JsonResponse({'error': 'Amount is required.'}, status=400)

            user_data = User.objects.get(username=user.username)
            email = user_data.email
            if not email:
                return JsonResponse({'error': 'User email is missing.'}, status=400)

            # Call initiate()
            paystack_response = initiate(email=email, amount=amount)

            # Extract actual data from JsonResponse
            if isinstance(paystack_response, JsonResponse):
                response_content = paystack_response.content
                parsed_data = json.loads(response_content)

                if 'error' in parsed_data:
                    return JsonResponse({'error': parsed_data['error']}, status=400)

                # Create transaction
                Transaction.objects.create(
                    wallet=user.wallet,
                    description=f"Fund Wallet - ₦{amount}",
                    amount=amount,
                    reference=parsed_data.get('reference'),
                    type=TransactionType.CREDIT,
                    mode=TransactionMode.DEPOSIT
                )

                return JsonResponse(parsed_data)
            else:
                return JsonResponse({'error': 'Unexpected response from Paystack.'}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



@csrf_exempt
def verify_payment(request, reference):
    if request.method == 'POST':
        try:
            transaction = Transaction.objects.get(reference=reference)
            response = verify(reference=reference)
            if  response.get('status') == TransactionStatus.SUCCESS.value:
                transaction.status = TransactionStatus.SUCCESS
                transaction.save()
                transaction.wallet.balance += transaction.amount
                transaction.wallet.save()
                messages.success(request, 'Payment verified successfully.')
            elif response.get('status') == TransactionStatus.CANCELED.value:
                transaction.status = TransactionStatus.CANCELED
                transaction.save()
                messages.error(request, 'Payment verification failed.')
            else:
                transaction.status = TransactionStatus.FAILED
                transaction.save()
                messages.error(request, 'Payment verification failed.')
            return JsonResponse({'status': 'success', 'message': 'Payment verified successfully.'})
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@login_required
def deposit(request):
    return render(request, 'wallet/deposit.html')

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

# def password_reset_request(request):
#     """Handle password reset request with OTP"""
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         if email:
#             try:
#                 user = User.objects.get(email=email)
#                 # Generate OTP
#                 otp = generate_otp()
                
#                 # Invalidate any existing OTPs for this user
#                 PasswordResetOTP.objects.filter(user=user).update(is_used=True)
                
#                 # Create new OTP
#                 PasswordResetOTP.objects.create(user=user, otp=otp)
                
#                 # Send OTP via email
#                 subject = "Password Reset OTP - SwiftPay"
#                 message = f"""
# Hello {user.username},

# You requested a password reset for your SwiftPay account.

# Your OTP code is: {otp}

# This OTP will expire in 15 minutes.

# If you didn't request this password reset, please ignore this email.

# Best regards,
# SwiftPay Team
#                 """
                
#                 try:
#                     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
#                     messages.success(request, f'OTP code has been sent to {email}. Please check your email.')
#                     return redirect('password_reset_verify')
#                 except Exception as e:
#                     messages.error(request, 'Error sending OTP. Please try again later.')
#                     return redirect('password_reset')
                    
#             except User.DoesNotExist:
#                 messages.error(request, 'No user found with this email address.')
#         else:
#             messages.error(request, 'Please enter your email address.')
    
#     return render(request, 'wallet/password_reset_request.html')

# def password_reset_verify(request):
#     """Handle OTP verification"""
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         otp = request.POST.get('otp')
        
#         if email and otp:
#             try:
#                 user = User.objects.get(email=email)
#                 otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).first()
                
#                 if otp_obj and otp_obj.is_valid():
#                     # Mark OTP as used
#                     otp_obj.is_used = True
#                     otp_obj.save()
                    
#                     # Store user email in session for password reset
#                     request.session['reset_email'] = email
#                     messages.success(request, 'OTP verified successfully. Please set your new password.')
#                     return redirect('password_reset_confirm')
#                 else:
#                     messages.error(request, 'Invalid or expired OTP. Please try again.')
#             except User.DoesNotExist:
#                 messages.error(request, 'User not found.')
#         else:
#             messages.error(request, 'Please enter both email and OTP.')
    
#     return render(request, 'wallet/password_reset_verify.html')

# def password_reset_confirm(request):
#     """Handle password reset confirmation with OTP"""
#     email = request.session.get('reset_email')
#     if not email:
#         messages.error(request, 'Please request a password reset first.')
#         return redirect('password_reset')
    
#     try:
#         user = User.objects.get(email=email)
#     except User.DoesNotExist:
#         messages.error(request, 'User not found.')
#         return redirect('password_reset')
    
#     if request.method == 'POST':
#         password1 = request.POST.get('password1')
#         password2 = request.POST.get('password2')
        
#         if password1 and password2:
#             if password1 == password2:
#                 if len(password1) >= 8:
#                     user.set_password(password1)
#                     user.save()
                    
#                     # Clear session
#                     if 'reset_email' in request.session:
#                         del request.session['reset_email']
                    
#                     messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
#                     return redirect('login')
#                 else:
#                     messages.error(request, 'Password must be at least 8 characters long.')
#             else:
#                 messages.error(request, 'Passwords do not match.')
#         else:
#             messages.error(request, 'Please fill in all fields.')
    
#     return render(request, 'wallet/password_reset_confirm.html', {'email': email})



