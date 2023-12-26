from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'amount',
            'transaction_type',
        ]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account') # account value ke pop kore anlam
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # ei field disable thakbe
        self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self): # amount field ke filter korbo
        min_deposit_amount = 100
        amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        if amount < min_deposit_amount:
            raise forms.ValidationError(
                f'You need to deposit at least {min_deposit_amount} $'
            )

        return amount


class WithdrawForm(TransactionForm):

    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance # 1000
        amount = self.cleaned_data.get('amount')
        if amount < min_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at least {min_withdraw_amount} $'
            )

        if amount > max_withdraw_amount:
            raise forms.ValidationError(
                f'You can withdraw at most {max_withdraw_amount} $'
            )

        if amount > balance: # amount = 5000, tar balance ache 200
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You can not withdraw more than your account balance'
            )

        return amount



class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        return amount
    
# ----------------------------------------------
# class TransferAmountForm(TransactionForm):
#     class Meta:
#         model = Transaction
#         fields = [
#             'account',
#             'amount',
#             # 'transaction_type',
#         ]

#     # def __init__(self, *args, **kwargs):
#     #     self.account = kwargs.pop('account') # account value ke pop kore anlam
#     #     super().__init__(*args, **kwargs)
#     #     self.fields['transaction_type'].disabled = True # ei field disable thakbe
#     #     self.fields['transaction_type'].widget = forms.HiddenInput() # user er theke hide kora thakbe

#     # def save(self, commit=True):
#     #     self.instance.account = self.account
#     #     self.instance.balance_after_transaction = self.account.balance
#     #     return super().save()
    

# # class TransferForm(TransactionForm):
# #     def clean(self): # _amount amount field ke filter korbo
# #         ac_no = self.cleaned_data.get('account.account_no')
# #         amount = self.cleaned_data.get('amount') # user er fill up kora form theke amra amount field er value ke niye aslam, 50
        
# #         min_transfer_amount = 100
# #         account = self.account #sender er account
# #         balance = account.balance #sender er account er balance

# #         if amount < min_transfer_amount:
# #             raise forms.ValidationError(
# #                 f'You can withdraw at least {min_transfer_amount} $'
# #             )
# #         if amount > balance: # amount = 5000, tar balance ache 200
# #             raise forms.ValidationError(
# #                 f'You have {balance} $ in your account. '
# #                 'You can not withdraw more than your account balance'
# #             )

# #         return {'ac_no': ac_no, 'amount': amount}
    
# class TransferForm(TransactionForm):
#     def clean(self):
#         # cleaned_data = super().clean()
#         ac_no = self.cleaned_data.get('account')
#         amount = self.cleaned_data.get('amount')
        
#         min_transfer_amount = 100
#         account = self.account
#         balance = account.balance

#         if amount < min_transfer_amount:
#             raise forms.ValidationError(
#                 f'You can transfer at least {min_transfer_amount} $'
#             )
#         if amount > balance:
#             raise forms.ValidationError(
#                 f'You have {balance} $ in your account. '
#                 'You cannot transfer more than your account balance'
#             )

#         return {'ac_no': ac_no, 'amount': amount}
    
from accounts.models import UserBankAccount

# class TransferForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = ['account', 'amount'] 
        
#     def clean(self):
#         cleaned_data = super().clean()
#         # account = cleaned_data.get('account')
#         amount = self.cleaned_data.get('amount')

#         min_transfer_amount = 100
#         user_account = self.account
#         balance = user_account.balance

#         if amount < min_transfer_amount:
#             raise forms.ValidationError(
#                 f'You can transfer at least {min_transfer_amount} $'
#             )
#         if amount > balance:
#             raise forms.ValidationError(
#                 f'You have {balance} $ in your account. '
#                 'You cannot transfer more than your account balance'
#             )

#         return cleaned_data
    
    
class TransferForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['account', 'amount', 'transaction_type']
        
    def clean(self):
        cleaned_data = super().clean()
        account = cleaned_data.get('account')
        amount = cleaned_data.get('amount')

        min_transfer_amount = 100

        if not account:
            raise forms.ValidationError('Invalid account.')

        user_account = account
        balance = user_account.balance 

        if amount < min_transfer_amount:
            raise forms.ValidationError(
                f'You can transfer at least {min_transfer_amount} $'
            )
        if amount > balance:
            raise forms.ValidationError(
                f'You have {balance} $ in your account. '
                'You cannot transfer more than your account balance'
            )

        return cleaned_data