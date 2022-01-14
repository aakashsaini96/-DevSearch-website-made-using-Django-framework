from django.core import paginator
from django.shortcuts import render, redirect
import re
#from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import Profile
#from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
#from django.db.models import Q
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from .utils import searchProjects, paginateProjects


def projects(request):
    all_projects, search_query = searchProjects(request)

    results = 6
    custom_range, all_projects = paginateProjects(request, all_projects, results)

    context = {'projects': all_projects, 'search_query': search_query,
     'custom_range': custom_range}

    return render(request, 'projects/projects.html', context)


def project(request, pk):
    projectObj = Project.objects.get(id=pk)

    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            profile = request.user.profile
            review.owner = profile
            review.project = projectObj
            form.save()

            projectObj.getVoteCount

            messages.success(request, 'Review submitted')
            return redirect('project', pk=projectObj.id)

    context = {'projectObj': projectObj, 'form': form}

    return render(request, 'projects/single-project.html', context)


@login_required(login_url="login")
def createProject(request):
    form = ProjectForm()
    profile = request.user.profile

    if request.method == 'POST':
        newtags = request.POST.get('newtags')
        tags = re.split(' , | ,|, |,', newtags)

        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            form.save()

            for tag in tags:
                tagg, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tagg)

            return redirect('user-account')
    
    context = {'form': form}
    return render(request, 'projects/project_form.html', context)


@login_required(login_url="login")
def updateProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id = pk)
    form = ProjectForm(instance=project)

    if request.method == 'POST':
        newtags = request.POST.get('newtags')
        tags = re.split(' , | ,|, |,', newtags)

        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save(commit=False)

            for tag in tags:
                tagg, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tagg)

            project.save()
            return redirect('user-account')
    
    context = {'form': form, 'project': project}
    return render(request, 'projects/project_form.html', context)


@login_required(login_url="login")
def deleteProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)

    if request.method == 'POST':
        project.delete()
        return redirect('user-account')

    context = {'object': project}
    return render(request, 'projects/delete_template.html', context)

#pk= pirmary key taken as string here in url

