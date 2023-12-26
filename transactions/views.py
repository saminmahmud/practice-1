from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.http import HttpResponse
from django.views.generic import CreateView, ListView
from transactions.constants import DEPOSIT, WITHDRAWAL,LOAN, LOAN_PAID
from datetime import datetime
from django.db.models import Sum
from transactions.forms import (
    DepositForm,
    WithdrawForm,
    LoanRequestForm,
    TransferForm,
)
from transactions.models import Transaction
from accounts.models import UserBankAccount

class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account': self.request.user.account
        })
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) # template e context data pass kora
        context.update({
            'title': self.title
        })

        return context


class DepositMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        # if not account.initial_deposit_date:
        #     now = timezone.now()
        #     account.initial_deposit_date = now
        account.balance += amount # amount = 200, tar ager balance = 0 taka new balance = 0+200 = 200
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )

        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = 'Withdraw Money'

    def get_initial(self):
        initial = {'transaction_type': WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')

        self.request.user.account.balance -= form.cleaned_data.get('amount')
        # balance = 300
        # amount = 5000
        self.request.user.account.save(update_fields=['balance'])

        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )

        return super().form_valid(form)

class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = 'Request For Loan'

    def get_initial(self):
        initial = {'transaction_type': LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account,transaction_type=3,loan_approve=True).count()
        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")
        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )

        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = 'transactions/transaction_report.html'
    model = Transaction
    balance = 0 # filter korar pore ba age amar total balance ke show korbe
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account=self.request.user.account
        )
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        else:
            self.balance = self.request.user.account.balance
       
        return queryset.distinct() # unique queryset hote hobe
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account': self.request.user.account
        })

        return context
    
        
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        print(loan)
        if loan.loan_approve:
            user_account = loan.account
                # Reduce the loan amount from the user's balance
                # 5000, 500 + 5000 = 5500
                # balance = 3000, loan = 5000
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approved = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('transactions:loan_list')
            else:
                messages.error(
            self.request,
            f'Loan amount is greater than available balance'
        )

        return redirect('loan_list')


class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' # loan list ta ei loans context er moddhe thakbe
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account,transaction_type=3)
        print(queryset)
        return queryset


# class Transfer_amountView(View):
#     model = TransferForm
#     template_name = 'transactions/transfer_amount.html'
#     # pk_url_kwargs = 'id'
from django.shortcuts import render
# from .forms import TransferForm

# def Transfer_amountView(request):
#     if request.method == 'POST':
#         form = TransferForm(request.POST)
#         if form.is_valid():
#             # Your validation logic is in the clean method of the form
#             # No need to perform additional validation here
#             transfer_data = form.clean()
#             # Process the transfer_data as needed
#             return render(request, 'success.html', {'transfer_data': transfer_data})
#     else:
#         form = TransferForm()
#     return render(request, 'transactions/transfer_amount.html', {'form': form})

# class Transfer_amountView(CreateView):
#     template_name = 'transactions/transfer_amount.html'
#     title = 'Transfer Amount Form'
#     success_url = reverse_lazy('transfer')

#     def get(self, request):
#         form = TransferForm()
#         return render(request, self.template_name, {'form': form})
    
#     def form_valid(self,form):
#         def get_queryset(self):
#             user_account = self.request.user.account
    
#     def form_valid(self, form):
#         account = form.cleaned_data.get('account')
#         amount = form.cleaned_data.get('amount')
#         print(form.cleaned_data)  #
#         user_account = self.request.user.account
#         user_account.balance -= amount 
#         # res_account = account.objects.filter(account=account)
#         res_account = Transaction.objects.filter(account_no=account).first()
#         res_account.balance += amount
#         user_account.save(
#             update_fields=[
#                 'balance'
#             ]
#         )
#         res_account.save(
#             update_fields=[
#                 'balance'
#             ]
#         )
#         messages.success(
#             self.request,
#             f'{"{:,.2f}".format(float(amount))}$ was transferd successfully'
#         )

        # return super().form_valid(form)
    
    # def post(self, request):
    #     form = TransferForm(self.request.POST)
    #     if form.is_valid():
    #         account = form.cleaned_data.get('account')
    #         amount = form.cleaned_data.get('amount')

    #         user_account = request.user.account
    #         recipient_account = UserBankAccount.objects.filter(account_no=account).first()

    #         if not recipient_account:
    #             messages.error(request, 'Recipient account not found.')
    #             return redirect('transfer_amount')

    #         if user_account.balance < amount:
    #             messages.error(request, 'Insufficient balance.')
    #             return redirect('transfer_amount')

    #         user_account.balance -= amount 
    #         recipient_account.balance += amount

    #         user_account.save(update_fields=['balance'])
    #         recipient_account.save(update_fields=['balance'])

    #         messages.success(
    #             request,
    #             f'{"{:,.2f}".format(float(amount))}$ was transferred successfully'
    #         )
    #         return redirect('transfer')

    #     return render(request, self.template_name, {'form': form})
    
    # def post(self, request):
    #     form = TransferForm(request.POST)
    #     if form.is_valid():
    #         # transfer_data = form.clean()
    #         account = form.cleaned_data.get('account')
    #         amount = form.cleaned_data.get('amount')

    #         user_account = request.user.account
    #         user_account.balance -= amount 
    #         res_account = UserBankAccount.objects.filter(account_no=account).first()
    #         res_account.balance += amount
    #         user_account.save(
    #             update_fields=[
    #                 'balance'
    #             ]
    #         )
    #         res_account.save(
    #             update_fields=[
    #                 'balance'
    #             ]
    #         )

    #         messages.success(
    #             request,
    #             f'{"{:,.2f}".format(float(amount))}$ was transferd successfully'
    #         )
    #         return render(request, 'transactions/transfer_amount.html', {'form': form})
    #     return render(request, self.template_name, {'form': form})

class Transfer_amountView(View):
    template_name = 'transactions/transfer_amount.html'

    def get(self, request):
        form = TransferForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TransferForm(request.POST)
        if form.is_valid():
            account_number = form.cleaned_data.get('account')
            amount = form.cleaned_data.get('amount')
            
            user_account = request.user.account
            recipient_account = UserBankAccount.objects.filter(account_no=account_number).first()

            if not recipient_account:
                messages.error(request, 'Recipient account not found.')
                return redirect('transfer')

            if user_account.balance < amount:
                messages.error(request, 'Insufficient balance.')
                return redirect('transfer')
            else:
                user_account.balance -= amount 
                recipient_account.balance += amount
                print(recipient_account.balance)

                user_account.save(update_fields=['balance'])
                recipient_account.save(update_fields=['balance'])

                messages.success(request, f'Transfer of {amount}$ was successful.')
                return redirect('transfer')

        return render(request, self.template_name, {'form': form})