from celery import Celery
from celery.schedules import crontab
from celery.decorators import periodic_task
from datetime import timedelta, datetime, date, timezone
from .models import Subscription, Invoice
from django.db import transaction
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# @periodic_task(run_every=crontab(minute=10, hour=0)) 
@periodic_task(run_every=crontab(minute='*', hour='*'))
def generate_invoices_for_subscriptions():
    try:
        today = datetime.now().date()
        # For testing Purpose
        # plan_requested_day = today - timedelta(days=1)

        subscriptions_to_invoice = Subscription.objects.filter(
            status='inactive', requested_on=today
        )

        with transaction.atomic():
            for subscription in subscriptions_to_invoice:
                existing_invoice = Invoice.objects.filter(
                    subscription=subscription, 
                    status='pending'
                ).exists()

                if existing_invoice:
                    logger.info(f"Invoice already exists for subscription {subscription.user.email}. Skipping.")
                    continue

                invoice = Invoice(
                    user=subscription.user,
                    plan=subscription.plan,
                    amount=subscription.plan.price,
                    issue_date=subscription.start_date - timedelta(days=7),
                    due_date=subscription.start_date - timedelta(days=3),
                    status='pending',
                    subscription=subscription
                )
                invoice.save()

        logger.info(f'{len(subscriptions_to_invoice)} invoices generated.')

    except Exception as err:
        logger.error(f'Error in generate_invoices_for_subscriptions Error:{repr(err)}')

# @periodic_task(run_every=crontab(minute=10, hour=2)) 
@periodic_task(run_every=crontab(minute='*', hour='*'))
def mark_overdue_invoices():
    try:
        today = datetime.now().date()
        overdue_invoices = Invoice.objects.filter(due_date__lt=today, status='pending')
        logger.info(f"Found {overdue_invoices.count()} overdue invoices to update.")
        overdue_invoices.update(status='overdue')
        logger.info("Overdue invoices updated successfully.")
    except Exception as err:
        logger.error(f'Error in mark_overdue_invoices Error:{repr(err)}')


# @periodic_task(run_every=crontab(minute=10, hour=1)) 
@periodic_task(run_every=crontab(minute='*', hour='*'))
def send_invoice_reminder():
    try:
        unpaid_invoices = Invoice.objects.filter(due_date__lte=datetime.now()).exclude(status="paid")
        for invoice in unpaid_invoices:
            try:
                user = invoice.user
                if user.email:
                    # send_mail(
                    #     'Invoice Payment Reminder',
                    #     f'Hi {user.username},\n\nYour invoice for PLAN:{invoice.subscription.plan.name} is still unpaid. Please make payment.',
                    #     'sbs@billing.com',
                    #     [user.email],
                    #     fail_silently=False,
                    # )
                    print(f'Reminder email sent to {user.email} for invoice {invoice.subscription.plan.name}.')
            except Exception as err:
                # If an error occurs while processing a specific user's invoice, it should not affect the processing of other users' invoices.
                logger.error(f'Error in send_invoice_reminder User Email:{user.email} Error:{repr(err)}')
    except Exception as err:
        logger.error(f'Error in send_invoice_reminder Error:{repr(err)}')


# @periodic_task(run_every=crontab(minute=10, hour=3)) 
@periodic_task(run_every=crontab(minute='*', hour='*'))
def cancel_overdue_subscriptions():
    try:
        today = datetime.now().date()
        overdue_invoices = Invoice.objects.filter(due_date__lt=today, status='overdue')
        with transaction.atomic():
            for invoice in overdue_invoices:
                subscription = invoice.subscription
                if subscription.start_date == today:
                    subscription.status = 'cancelled'
                    subscription.save()
                    invoice.status = 'cancelled'
                    invoice.save()
                    logger.info(f"Subscription {subscription.user.email} has been cancelled due to overdue invoice.")
                else:
                    logger.info(f"Subscription {subscription.user.email} is not eligible for cancellation today.")

        logger.info(f"Processed {len(overdue_invoices)} overdue invoices for cancellation.")

    except Exception as err:
        logger.error(f'Error in cancel_overdue_subscriptions Error:{repr(err)}')


# @periodic_task(run_every=crontab(minute=10, hour=4)) 
@periodic_task(run_every=crontab(minute='*', hour='*'))
def mark_subscriptions_as_expired():
    try:
        end_today = datetime.now().date() - timedelta(days=1) ## user should use plan till last date
        subscriptions_to_expire = Subscription.objects.filter(end_date=end_today, status='active')
        with transaction.atomic():
            for subscription in subscriptions_to_expire:
                subscription.status = 'expired'
                subscription.save()
                logger.info(f"Subscription {subscription.user.email} has been marked as expired.")

        logger.info(f"Processed {len(subscriptions_to_expire)} subscriptions for expiration.")

    except Exception as err:
        logger.error(f'Error in mark_subscriptions_as_expired Error:{repr(err)}')