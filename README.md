# Mobile Wallet Application

A Django-based mobile wallet application with deposit, transfer, airtime, and data purchase functionality.

## Features

- **User Authentication**: Login, signup, logout, and password reset functionality
- **Wallet Management**: View balance and transaction history
- **Deposit Funds**: Two deposit options available:
  - **Direct Deposit**: Simple form that directly adds funds to wallet (for testing)
  - **Paystack Integration**: Secure payment processing via Paystack
- **Money Transfer**: Send money to other users
- **Airtime Purchase**: Buy airtime for different networks
- **Data Purchase**: Purchase data plans for different networks
- **Password Reset**: Secure OTP-based password recovery system

## Deposit Functionality

The deposit feature has been updated to automatically determine the logged-in user without requiring manual user input. Here's how it works:

### Automatic User Detection
- The deposit view uses `@login_required` decorator to ensure only authenticated users can access it
- The logged-in user is automatically retrieved using `request.user`
- The user's wallet is found using `get_object_or_404(Wallet, user=request.user)`
- No manual user selection is required

### Deposit Options

1. **Direct Deposit (Primary)**
   - Simple form that directly adds funds to the user's wallet
   - Perfect for testing and development
   - No external payment processing required

2. **Paystack Integration (Optional)**
   - Secure payment processing via Paystack
   - Requires Paystack API keys to be configured
   - Automatically uses the logged-in user's email for payment

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Paystack (Optional)**
   - Add your Paystack API keys to `mobile_wallet/settings.py`:
   ```python
   PAYSTACK_PUBLIC_KEY = 'your_paystack_public_key_here'
   PAYSTACK_SECRET_KEY = 'your_paystack_secret_key_here'
   ```

3. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start the Server**
   ```bash
   python manage.py runserver
   ```

## Usage

1. **Register/Login**: Create an account or login with existing credentials
2. **Password Reset**: 
   - Click "Forgot Password?" on the login page
   - Enter your email address to receive an OTP
   - Enter the 6-digit OTP code sent to your email
   - Set your new password
   - OTP expires in 15 minutes for security
3. **Deposit Funds**: 
   - Go to the deposit page
   - Enter the amount you want to deposit
   - Choose between direct deposit or Paystack payment
   - The system automatically uses your logged-in account
4. **View Balance**: Check your current balance on the home page
5. **Transfer Money**: Send money to other users
6. **Buy Services**: Purchase airtime or data plans

## Security Features

- All views are protected with `@login_required` decorator
- CSRF protection enabled
- User authentication required for all wallet operations
- Automatic user detection prevents unauthorized access

## File Structure

```
mobile_wallet/
├── wallet/
│   ├── views.py          # Main application logic
│   ├── models.py         # Database models
│   ├── urls.py           # URL routing
│   └── templates/        # HTML templates
├── mobile_wallet/
│   ├── settings.py       # Django settings
│   └── urls.py           # Main URL configuration
└── manage.py             # Django management script
```

## Key Changes Made

1. **Removed duplicate deposit function** in `views.py`
2. **Added automatic user detection** using `request.user`
3. **Enhanced deposit template** with both direct and Paystack options
4. **Added payment verification** endpoint for Paystack integration
5. **Installed requests library** for API calls
6. **Added Paystack configuration** to settings
7. **Implemented OTP-based password reset** system with email verification
8. **Added PasswordResetOTP model** for secure OTP management
9. **Created OTP verification templates** with Tailwind CSS styling
10. **Added session-based password reset** flow for enhanced security 