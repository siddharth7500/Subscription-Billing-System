from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from .models import Subscription, Invoice, Plan
from django.http import JsonResponse
import datetime
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import logging
logging.basicConfig(level=logging.DEBUG)  
logger = logging.getLogger(__name__)


class MyPlanAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response_data = {}
        try:
            user = request.user
            subscriptions = Subscription.objects.filter(user=user)
            active_subscription = subscriptions.filter(status="active").last()
            if active_subscription:
                response_data['active_plan'] = {
                    'plan_name': active_subscription.plan.name,
                    'plan_price': active_subscription.plan.price,
                    'status': active_subscription.status.capitalize(),
                    'start_date': active_subscription.start_date.strftime('%d %b %Y'),
                    'end_date': active_subscription.end_date.strftime('%d %b %Y')
                }
            else:
                inactive_subscription = subscriptions.filter(status="inactive").last()
                if inactive_subscription:
                    response_data['active_plan'] = {
                        'plan_name': inactive_subscription.plan.name,
                        'plan_price': inactive_subscription.plan.price,
                        'status': 'Pending Activation',
                        'start_date': inactive_subscription.start_date.strftime('%d %b %Y'),
                        'end_date': inactive_subscription.end_date.strftime('%d %b %Y')
                    } 
                else:
                    response_data['active_plan'] = {'error': 'No active subscription found.'}

            # Prepare past plans data
            past_plans_data = []
            for subscription in subscriptions.exclude(status__in=['active', 'inactive']):
                past_plans_data.append({
                    'plan_name': subscription.plan.name,
                    'plan_price': subscription.plan.price,
                    'status': subscription.status.capitalize(),
                    'start_date': subscription.start_date.strftime('%d %b %Y'),
                    'end_date': subscription.end_date.strftime('%d %b %Y'),
                    'cancelled_on': subscription.cancelled_on.strftime('%d %b %Y')
                })

            response_data['past_plans'] = past_plans_data
        except Exception as err:
            logger.error(f'Error in get MyPlanAPIView Error:{repr(err)}')
        return Response(response_data)


class MyInvoicesAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        response_data = {}
        try:
            user = request.user
            invoices = Invoice.objects.filter(user=user)
            active_invoice = invoices.filter(subscription__status="active").last()
            if active_invoice:
                if active_invoice.subscription:
                    response_data['active_invoice'] = {
                        'plan_name': active_invoice.subscription.plan.name,
                        'plan_price': active_invoice.subscription.plan.price,
                        'start_date': active_invoice.subscription.start_date.strftime('%d %b %Y'),
                        'end_date': active_invoice.subscription.end_date.strftime('%d %b %Y'),
                        'amount': active_invoice.amount,
                        'issue_date': active_invoice.issue_date,
                        'due_date': active_invoice.due_date,
                        'status': active_invoice.status
                    }
            else:
                inactive_invoice = invoices.filter(subscription__status="inactive").last()
                if inactive_invoice:
                    if inactive_invoice.subscription:
                        response_data['active_invoice'] = {
                            'plan_name': inactive_invoice.subscription.plan.name,
                            'plan_price': inactive_invoice.subscription.plan.price,
                            'start_date': inactive_invoice.subscription.start_date.strftime('%d %b %Y'),
                            'end_date': inactive_invoice.subscription.end_date.strftime('%d %b %Y'),
                            'amount': inactive_invoice.amount,
                            'issue_date': inactive_invoice.issue_date,
                            'due_date': inactive_invoice.due_date,
                            'status': inactive_invoice.status
                        }
                else:
                    response_data['active_invoice'] = {'error': 'No active subscription found.'}

            past_invoices_data = []
            for invoice in invoices.exclude(subscription__status__in=["active", "inactive"]):
                if invoice.subscription:
                    past_invoices_data.append({
                        'plan_name': invoice.subscription.plan.name,
                        'plan_price': invoice.subscription.plan.price,
                        'status': invoice.subscription.status.capitalize(),
                        'start_date': invoice.subscription.start_date.strftime('%d %b %Y'),
                        'end_date': invoice.subscription.end_date.strftime('%d %b %Y'),
                        'cancelled_on': invoice.subscription.cancelled_on.strftime('%d %b %Y'),
                        'amount': invoice.amount,
                        'issue_date': invoice.issue_date,
                        'due_date': invoice.due_date,
                        'status': invoice.status
                    })
            response_data['past_invoices_data'] = past_invoices_data
        except Exception as err:
            logger.error(f'Error in get MyInvoicesAPIView Error:{repr(err)}')
        return Response(response_data)


class PaymentStatusAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        invoice_data = {}
        try:
            user = request.user
            pending_invoices = Invoice.objects.filter(user=user, status='pending').order_by('issue_date')
            paid_invoices = Invoice.objects.filter(user=user, status='paid').order_by('issue_date')
            overdue_invoices = Invoice.objects.filter(user=user, status='overdue').order_by('issue_date')
            cancelled_invoices = Invoice.objects.filter(user=user, status='cancelled').order_by('issue_date')

            invoice_data = {
                'pending_invoices': self.get_invoice_details(pending_invoices),
                'paid_invoices': self.get_invoice_details(paid_invoices),
                'overdue_invoices': self.get_invoice_details(overdue_invoices),
                'cancelled_invoices': self.get_invoice_details(cancelled_invoices),
            }
        except Exception as err:
            logger.error(f'Error in get PaymentStatusAPIView Error:{repr(err)}')
        return Response(invoice_data)

    def get_invoice_details(self, invoices):
        invoice_details = []
        try:
            for invoice in invoices:
                subscription = invoice.subscription
                plan = subscription.plan
                invoice_details.append({
                    'invoice_id': invoice.id,
                    'plan_name': plan.name.upper(),
                    'plan_price': plan.price,
                    'amount': invoice.amount,
                    'issue_date': invoice.issue_date.strftime('%d %b %Y'),
                    'due_date': invoice.due_date.strftime('%d %b %Y'),
                    'status': invoice.status,
                    'subscription_status': subscription.status.capitalize(),
                    'subscription_start_date': subscription.start_date.strftime('%d %b %Y'),
                    'subscription_end_date': subscription.end_date.strftime('%d %b %Y'),
                    'subscription_cancelled_on': subscription.cancelled_on.strftime('%d %b %Y') if subscription.status == 'cancelled' else 'N/A'
                })
        except Exception as err:
            logger.error(f'Error in get_invoice_details Error:{repr(err)}')
        return invoice_details



@login_required(login_url='/login/')
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated]) 
def select_plan(request):
    plan_id = request.data.get('plan_id')
    if not plan_id:
        return Response({'error': 'No plan ID provided.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        plan = Plan.objects.get(id=plan_id)

        current_subscription = Subscription.objects.filter(user=request.user, status__in=['active','inactive'])

        if current_subscription:
            Invoice.objects.filter(user=request.user, subscription__in=current_subscription).update(status="cancelled")
            current_subscription.update(status='cancelled')

        new_subscription = Subscription(
            user=request.user,
            plan=plan,
            requested_on=datetime.datetime.now().date(),
            start_date=datetime.datetime.now().date() + datetime.timedelta(days=7),
            end_date=datetime.datetime.now().date() + datetime.timedelta(days=7) + datetime.timedelta(days=30),
            status='inactive'
        )
        new_subscription.save()

        return Response({'message': 'Subscription updated successfully.'}, status=status.HTTP_200_OK)

    except Plan.DoesNotExist:
        return Response({'error': 'Plan not found.'}, status=status.HTTP_404_NOT_FOUND)