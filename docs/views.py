from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .models import Room

# Create your views here.
@login_required(login_url='/login/')
def ide(request):
    return render(request, 'docs/ide.html') 


@login_required(login_url='/login/')
def create_project(request):
    if request.method == 'POST':
        name = request.POST['project_name']
        description = request.POST.get('description', '')
        
        slug = slugify(name)
        
        # Create new Room object with generated slug
        project = Room.objects.create(name=name, slug=slug, description=description)
        return redirect('/docs/view_projects/')
    else:
        return render(request, 'docs/create_project.html')



@login_required(login_url='/login/')
def view_projects(request):
    projects = Room.objects.all()

    return render(request, 'docs/view_projects.html', {'projects': projects})

@login_required(login_url='/login/')
def project_ide(request, slug):
    project = get_object_or_404(Room, slug=slug)
    return render(request, 'docs/ide.html', {'project': project})