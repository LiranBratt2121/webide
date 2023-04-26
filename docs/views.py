from django.shortcuts import render

# Create your views here.
def ide(request):
    return render(request, 'docs/ide.html') 


def create_project(request):
    return render(request, 'docs/create_project.html')