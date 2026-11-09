from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User as AuthUser
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages


def _get_selected_role(request):
    role = (request.POST or request.GET).get('role', '').strip().lower()
    if role == 'admin':
        return 'admin'
    if request.path.startswith('/admin/'):
        return 'admin'
    return 'customer'


def login_view(request):
    selected_role = _get_selected_role(request)

    if request.user.is_authenticated:
        if request.user.is_staff and selected_role == 'admin':
            return redirect('admin_dashboard')
        return redirect(request.GET.get('next') or 'home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'customer').strip().lower()
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'cinemaseat/login.html', {'selected_role': role})

        if role == 'admin' and not user.is_staff:
            messages.error(request, 'Admin access only. Please sign in with a staff account.')
            return render(request, 'cinemaseat/login.html', {'selected_role': role})

        login(request, user)
        if role == 'admin':
            return redirect('admin_dashboard')
        return redirect(request.POST.get('next') or request.GET.get('next') or 'home')

    return render(request, 'cinemaseat/login.html', {'selected_role': selected_role})


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
