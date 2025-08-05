from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'wallet_number', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__username', 'wallet_number')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'amount', 'reference', 'type', 'mode', 'status', 'created_at')
    list_filter = ('type', 'mode', 'status', 'created_at')
    search_fields = ('wallet__user__username', 'reference', 'description')
    ordering = ('-created_at',)



