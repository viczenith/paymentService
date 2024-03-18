from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
# from moneyApp.models import CustomUser
from django.conf import settings
CustomUser = settings.AUTH_USER_MODEL


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

# class CustomUser(AbstractUser):
    
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    CURRENCY_CHOICES = [
            ('GBP', 'British Pound'),
            ('USD', 'US Dollar'),
            ('EUR', 'Euro'),
        ]
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')

    groups = models.ManyToManyField(Group, related_name="customuser_groups", blank=True, verbose_name=_("user group"))
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions", blank=True, verbose_name=_("user permission"))

    objects = CustomUserManager()

    class Meta:
        permissions = [("can_view_dashboard", "Can view dashboard")]

class CustomUserGroups(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class CustomUserUserPermissions(models.Model):
    customuser = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)


from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    total_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

    currency = models.CharField(max_length=3, choices=[('USD', 'US Dollar'), ('GBP', 'British Pound'), ('EUR', 'Euro')], default='USD')

    def __str__(self):
        return f"Profile for {self.user.username}"


# Signal to create a profile for every new user
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Transfer', 'Transfer'),
    ]

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_transactions', null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)

    # Fields specific to deposit transactions
    deposit_source = models.CharField(max_length=50, blank=True, null=True)
    deposit_method = models.CharField(max_length=50, blank=True, null=True)

    # Fields specific to withdrawal transactions
    withdrawal_method = models.CharField(max_length=50, blank=True, null=True)

    # Fields specific to transfer transactions
    transfer_note = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.transaction_type == 'Deposit':
            return f"{self.sender} deposited {self.amount}"
        elif self.transaction_type == 'Withdrawal':
            return f"{self.sender} withdrew {self.amount}"
        elif self.transaction_type == 'Transfer':
            return f"{self.sender} transferred {self.amount} to {self.receiver.email}"
        else:
            return f"Unknown transaction type: {self.transaction_type}"
    

# class PaymentRequest(models.Model):
#     requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_requests_sent')
#     recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_requests_received')
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     description = models.CharField(max_length=100)
#     reason = models.CharField(max_length=255)
#     is_accepted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Payment Request from {self.requester} to {self.recipient} for {self.description}"


class PaymentRequest(models.Model):
    requester = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_requests_sent')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_requests_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment Request from {self.requester.username} to {self.recipient.username}"
