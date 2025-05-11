import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import  login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def home_view(request):
    from billing.models import Plan, Subscription
    plans = Plan.objects.all()
    if not plans:
        Plan.objects.create(name='enterprise', price=250)
        Plan.objects.create(name='pro', price=150)
        Plan.objects.create(name='basic', price=100)
        
    data = []
    for plan in plans:
        is_selected = Subscription.objects.filter(
            user=request.user,
            end_date__gte=datetime.datetime.now().date(),
            plan=plan
        )

        plan_data = {
            'id': plan.id,
            'plan_name': plan.name,
            'plan_price': plan.price,
            'is_selected': is_selected.filter(status="active").exists(),
            'yet_to_activate': is_selected.filter(status="inactive").exists()
        }
        data.append(plan_data)
    return render(request, 'users/home.html', {'plans': data})


def login_view(request):
    error_message = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            error_message = "Invalid username or password. Please try again."
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form, 'error_message': error_message})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm({"username":request.POST['username'], "password1":request.POST['password'], "password2":request.POST['password']})

        if form.is_valid():
            user = form.save()
            user.email = request.POST.get('email')
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login') 