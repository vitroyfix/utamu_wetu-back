from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
   
    coins = models.PositiveIntegerField(default=0, help_text="Loyalty points earned from purchases")
    is_subscribed = models.BooleanField(default=True, help_text="For marketing emails and updates")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        return f"Profile: {getattr(self.user, 'email', self.user.username)} ({self.coins} coins)"

class Address(models.Model):
    ADDRESS_TYPES = (
        ('HOME', 'Home'),
        ('OFFICE', 'Office'),
        ('OTHER', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    county = models.CharField(max_length=100, default="Nairobi")
    estate = models.CharField(max_length=100, help_text="e.g. Nyayo Estate, Gate 2")
    house_number = models.CharField(max_length=100, help_text="e.g. Hse 12, Apt 4B")
    street_address = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='HOME')

    class Meta:
        verbose_name_plural = "Addresses"

    def save(self, *args, **kwargs):
       
        if self.is_default:
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.estate} - {self.house_number}"

class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Value of the discount")
    is_percentage = models.BooleanField(default=False, help_text="If checked, discount is treated as %")
    
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True) # Allow null during creation
    
    active = models.BooleanField(default=True)
    limit = models.PositiveIntegerField(default=1, help_text="Total usage limit for this voucher")

    def __str__(self):
        type_str = "%" if self.is_percentage else "KES"
        return f"{self.code} - {self.discount_amount}{type_str}"

    @property
    def is_valid(self):
        """Checks if the voucher can be applied based on status and dates."""
        if not self.active:
            return False
            
        now = timezone.now()
        
        if self.valid_from and self.valid_to:
            return self.valid_from <= now <= self.valid_to
        
        return False

class VoucherUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher = models.ForeignKey(Voucher, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'voucher')

@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)