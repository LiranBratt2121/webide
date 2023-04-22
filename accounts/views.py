from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import User
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models import Q

# Create your views here.
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        school = request.POST['school']
        password = request.POST['password']
        confirm_pass = request.POST['confirm-pass']

        account = User.objects.create_user(username=username, email=email, password=password)
        
        account.save()
        
        messages.success(request, 'You Successfully Registered An Account :D')
             
        return redirect('login_user')
    
    return render(request, 'accounts/register.html')


def login_user(request):
    if request.method == 'POST':
        username_or_email = request.POST['username']
        password = request.POST['password']
        
        user = User.objects.filter(Q(username=username_or_email) | Q(email=username_or_email)).first()
        
        if user and user.check_password(password):
            login(request, user)
            
            return render(request, 'home.html', {'username': user.username})

        else:
            messages.error(request, "Try Again!")
            
            return redirect('login_user')
           
    return render(request, 'accounts/login.html')
    
        
def home(request):
    return render(request, 'home.html', {'user': request.user})
