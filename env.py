import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
PASSWORD_RESET_TIMEOUT = os.getenv('PASSWORD_RESET_TIMEOUT')
PAYSTACK_PUBLIC_KEY =  os.getenv('PAYSTACK_PUBLIC_KEY') # Replace with your actual Paystack public key
PAYSTACK_SECRET_KEY =  os.getenv('PAYSTACK_SECRET_KEY') # Replace with your actual Paystack secret key
