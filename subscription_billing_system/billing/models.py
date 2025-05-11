from datetime import timedelta
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Plan(models.Model):
    PLAN_CHOICES = [('basic', 'Basic'), ('pro', 'Pro'), ('enterprise', 'Enterprise')]
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [('inactive', 'Inactive') , ('active', 'Active'), ('cancelled', 'Cancelled'), ('expired', 'Expired')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    requested_on = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inactive')
    cancelled_on = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.user} - {self.plan.name}"
    
    # def save(self, *args, **kwargs):
    #     if not self.pk and self.status == 'inactive':
    #         super().save(*args, **kwargs)
    #         self.create_invoice()
    #     else:
    #         super().save(*args, **kwargs)

    # def create_invoice(self):
    #     invoice = Invoice(
    #         user=self.user,
    #         plan=self.plan,
    #         amount=self.plan.price,
    #         issue_date=self.start_date - timedelta(days=7),
    #         due_date=self.start_date,
    #         status='pending',
    #         subscription=self
    #     )
    #     invoice.save()


class Invoice(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices', null=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.user}"
