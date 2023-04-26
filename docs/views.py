from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Room

# Create your views here.
def ide(request):
    return render(request, 'docs/ide.html') 

@login_required
def create_project(request):
    return render(request, 'docs/create_project.html')

@login_required
def view_projects(request):
    projects = Room.objects.all()

    return render(request, 'docs/view_projects.html', {'projects': projects})

@login_required
def project_ide(request, slug):
    project = Room.objects.get(slug=slug)

    return render(request, 'docs/ide.html', {'project': project})