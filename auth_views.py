from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated: return redirect(request.GET.get('next') or 'home')
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user); return redirect('home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'cinemaseat/login.html')

def signup_view(request):
    if request.user.is_authenticated: return redirect('home')
    if request.method == 'POST':
        name=request.POST.get('name','').strip(); email=request.POST.get('email','').strip(); password=request.POST.get('password',''); confirm=request.POST.get('confirm','')
        if not name or not email or not password: messages.error(request,'Please complete all required fields.')
        elif password != confirm: messages.error(request,'Passwords do not match.')
        elif AuthUser.objects.filter(username=email).exists(): messages.error(request,'An account with this email already exists.')
        else:
            user=AuthUser.objects.create_user(username=email,email=email,password=password,first_name=name)
            login(request,user); return redirect(request.POST.get('next') or request.GET.get('next') or 'home')
    return render(request,'cinemaseat/signup.html')

def logout_view(request): logout(request); return redirect('login')
