
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'), 
    path('deposit/', views.deposit, name='deposit'),
    path('verify/<str:reference>/', views.verify_payment, name='verify_payment'),
    path('transfer/', views.transfer, name='transfer'),
    path('airtime/', views.buy_airtime, name='buy_airtime'),
    path('data/', views.buy_data, name='buy_data'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('verify-account/', views.verify_account, name='verify_account'),
    # path('password-reset/', views.password_reset_request, name='password_reset'),
    # path('password-reset-verify/', views.password_reset_verify, name='password_reset_verify'),
    # path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    path('fund-wallet', views.fund_wallet, name='fund_wallet'),  
    path('fund-wallet/verify/', views.verify_payment, name='fund_wallet_verify'),
]
