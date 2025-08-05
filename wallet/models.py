from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from enum import Enum
import random

def generate_account_number():
    while True:
        number = str(random.randint(1000000000, 9999999999))  # 10-digit number
        if not Wallet.objects.filter(wallet_number=number).exists():
            return number

class TransactionMode(str, Enum):
    AIRTIME = 'airtime'
    DATA = 'data'
    TRANSFER = 'transfer'
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'

    @classmethod
    def choices(cls):
        return [(key.value, key.value.capitalize()) for key in cls]


class TransactionType(str, Enum):
    DEBIT = 'debit'
    CREDIT = 'credit'

    @classmethod
    def choices(cls):
        return [(key.value, key.value.capitalize()) for key in cls]


class TransactionStatus(str, Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    CANCELED = 'cancelled'
    REVERSED = 'reversed'

    @classmethod
    def choices(cls):
        return [(key.value, key.value.capitalize()) for key in cls]


class Wallet(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    wallet_number = models.CharField(max_length=10, unique=True, null=True, blank=True, default=generate_account_number)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=15, unique=True, null=True, blank=True)
    type = models.CharField(max_length=15, choices=TransactionType.choices())
    mode = models.CharField(max_length=20, choices=TransactionMode.choices(), null=True, blank=True)
    status = models.CharField(max_length=15, choices=TransactionStatus.choices(), default=TransactionStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.type} - {self.amount}"

