from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Transaction
from .forms import TransactionForm, CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.generic.edit import CreateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from .models import CustomUser
from .forms import DepositForm
from .models import Profile
import os
from django.core.wsgi import get_wsgi_application

from django.contrib import messages

from .forms import TransactionForm
from django.contrib.auth import logout
from django.urls import reverse
from django.db.models import Sum
from django import forms
from django.db import transaction
import logging
from decimal import Decimal

from .models import PaymentRequest
from .forms import PaymentRequestForm

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
application = get_wsgi_application()



def home(request):
    return render(request, 'home.html')



def transfer_money(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)

            if transaction.amount > request.user.profile.total_balance:
                messages.error(request, 'Insufficient balance. Please check your balance.')
                return redirect('transfer_money')

            transaction.sender = request.user
            transaction.balance_after_transaction = request.user.profile.total_balance - transaction.amount
            transaction.receiver = form.cleaned_data['receiver_email']
            
            
            # Determine transaction type
            if transaction.amount > 0:
                transaction.transaction_type = 'Deposit'
            elif transaction.amount < 0:
                transaction.transaction_type = 'Withdrawal'
            else:
                transaction.transaction_type = 'Transfer'
            
            transaction.save()

            # Update sender's balance
            request.user.profile.total_balance = transaction.balance_after_transaction
            request.user.profile.save()

            # Update receiver's balance if applicable
            transaction.receiver.profile.total_balance += transaction.amount
            transaction.receiver.profile.save()

            messages.success(request, f'Transaction successful! Your money has been transferred. ${transaction.amount}')

            return redirect('transfer_money')

    else:
        form = TransactionForm()

    return render(request, 'transfer_money.html', {'form': form})



def transaction_history(request):
    if request.user.is_authenticated:
        transactions = Transaction.objects.filter(sender=request.user)
        return render(request, 'transaction_history.html', {'transactions': transactions})
    else:
        pass


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        # Define conversion rates
        GBP_to_USD_rate = 1.37
        EUR_to_USD_rate = 1.21

        if form.is_valid():
            user = form.save(commit=False)
            user.save()  # Save the user first to ensure the user instance exists
            
            # Check if user profile exists, create if not
            if hasattr(user, 'profile'):
                profile = user.profile
            else:
                profile = Profile.objects.create(user=user)

            # Set initial balance based on selected currency
            currency = request.POST.get('currency')
            if currency == 'GBP':
                profile.total_balance = 1000 * GBP_to_USD_rate
            elif currency == 'EUR':
                profile.total_balance = 1000 * EUR_to_USD_rate
            else:
                profile.total_balance = 1000
            
            profile.save()
            
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('profile')
        else:
            # Display form errors as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})


from .forms import CustomUserCreationForm
def change_currency(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            currency = form.cleaned_data['currency']
            user = request.user
            profile = user.profile
            profile.currency = currency
            profile.save()
            messages.success(request, 'Currency changed successfully.')
            return redirect('profile')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
    else:
        form = CustomUserCreationForm(initial={'currency': request.user.profile.currency})
    
    return render(request, 'change_currency.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('/')



@login_required
def profile(request):
    user = request.user
    sent_transactions = Transaction.objects.filter(sender=user)
    received_transactions = Transaction.objects.filter(receiver=user)
    return render(request, 'profile.html', {'user': user, 'sent_transactions': sent_transactions, 'received_transactions': received_transactions})



class DepositForm(forms.Form):
    amount = forms.DecimalField(label='Amount', min_value=0, required=True)



@method_decorator(login_required, name='dispatch')
class DepositView(View):
    template_name = 'deposit_money.html'

    def get(self, request):
        form = DepositForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            if amount > 0:
                request.user.profile.total_balance += amount
                request.user.profile.save()

                Transaction.objects.create(
                    sender=request.user,
                    receiver=None,
                    amount=amount 
                )

                return redirect('profile')

        return render(request, self.template_name, {'form': form})



logger = logging.getLogger(__name__)



class WithdrawView(View):
    template_name = 'withdraw_money.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount')

        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("Withdrawal amount must be greater than zero.")

            user = request.user
            profile = Profile.objects.select_for_update().get(user=user)

            # To Ensure the user has sufficient balance
            if profile.total_balance >= amount:
                
                profile.total_balance -= amount
                profile.save()

                messages.success(request, f'Withdrawal of ${amount} successful!')
                return redirect('withdraw_money')
            
            else:
                messages.error(request, 'Insufficient funds for withdrawal.')
        except ValueError as e:
            logger.error(f"Invalid withdrawal amount: {e}")
            messages.error(request, 'Invalid withdrawal amount. Please enter a valid positive number.')
        except Profile.DoesNotExist:
            
            logger.error("User profile not found.")
            messages.error(request, 'User profile not found. Please contact support.')
        except Exception as e:
            
            logger.exception("An unexpected error occurred during withdrawal.")
            messages.error(request, 'An unexpected error occurred. Please try again later.')

        return render(request, self.template_name, {'messages': messages.get_messages(request)})



class ProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)



@login_required
def create_payment_request(request):
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            payment_request = form.save(commit=False)
            payment_request.requester = request.user
            payment_request.save()
            messages.success(request, 'Payment request created successfully.')
            return redirect('create_payment_requests')
        else:
            messages.error(request, 'Invalid form data. Please correct the errors.')
    else:
        form = PaymentRequestForm()
    return render(request, 'create_payment_request.html', {'form': form})

@login_required
def view_payment_requests(request):
    payment_requests = PaymentRequest.objects.filter(recipient=request.user).order_by('-id')
    return render(request, 'view_payment_requests.html', {'payment_requests': payment_requests})

@login_required
def accept_payment_request(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)

    if not payment_request.is_accepted:
        if payment_request.amount > payment_request.recipient.profile.total_balance:
            messages.error(request, 'Insufficient balance. Please check your balance.')
            return redirect('view_payment_requests')
        
        # Mark the payment request as accepted
        payment_request.is_accepted = True
        payment_request.save()

        
        # Credit the payment amount to the recipient's account
        payment_request.requester.profile.total_balance += payment_request.amount
        payment_request.requester.profile.save()

        # Deduct the payment amount from the sender's (requester's) account
        payment_request.recipient.profile.total_balance -= payment_request.amount
        payment_request.recipient.profile.save()

        messages.success(request, 'Payment request accepted successfully.')
    else:
        messages.error(request, 'Payment request has already been accepted.')

    return redirect('view_payment_requests')

@login_required
def reject_payment_request(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)

    if payment_request.is_accepted:
        messages.error(request, 'Cannot reject an already accepted payment request.')
    else:
        payment_request.delete()
        messages.success(request, 'Payment request rejected successfully.')

    return redirect('view_payment_requests')
