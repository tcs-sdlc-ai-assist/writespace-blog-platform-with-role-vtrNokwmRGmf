from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from accounts.forms import LoginForm, RegistrationForm


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin-panel/')
        return redirect('/blogs/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('/admin-panel/')
                return redirect('/blogs/')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin-panel/')
        return redirect('/blogs/')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            display_name = form.cleaned_data['display_name']
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=display_name,
            )
            login(request, user)
            return redirect('/blogs/')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('/')