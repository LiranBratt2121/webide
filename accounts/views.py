from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import SignUpForm

# Create your views here.
def signup(request):
    form = SignUpForm()

    if request.method == 'POST':   
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            form.save()
            
            user = form.save()
             
            login(request, user)
            
            return redirect('home')
        
    return render(request ,'accounts/signup.html', context= {'form': form})


def login_user(request):
    pass
    
        
def home(request):
    return render(request, 'home.html', {'user': request.user})
