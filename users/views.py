from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
#from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utils import searchProfiles, paginateProfiles
# Create your views here.


def loginUser(request):
    page = 'login'
    context = {'page': page}

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'user-account')
        else:
            messages.error(request, 'Username OR password is incorrect')

    return render(request, 'users/login_register.html', context)


def logoutUser(request):
    logout(request)
    messages.info(request, 'User successfully logged out')
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, "User account was created!")

            login(request, user)
            return redirect('update-profile')
        else:
            messages.error(request, "An error has occured during registeration!")

    context = {'page': page, 'form':form}
    return render(request, 'users/login_register.html', context)


def profiles(request):
    profiles, search_query = searchProfiles(request)

    results = 6
    custom_range, profiles = paginateProfiles(request, profiles, results)

    context = {'profiles': profiles, 'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'users/profiles.html', context)


def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)

    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")

    context = {'profile': profile, 'topSkills': topSkills, 'otherSkills': otherSkills}
    return render(request, 'users/user-profile.html', context)

@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile

    context = {'profile': profile}

    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def updateProfile(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user-account')

    context = {'form': form}

    return render(request, 'users/profile_form.html', context)


@login_required(login_url='login')
def addSkill(request):
    form = SkillForm()
    profile = request.user.profile

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            form.save()
            messages.success(request, "New skill was added!")
            return redirect('user-account')

    context = {'form': form}

    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, "Skill was updated!")
            return redirect('user-account')

    context = {'form': form}

    return render(request, 'users/skill_form.html', context)


@login_required(login_url="login")
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)

    if request.method == 'POST':
        skill.delete()
        messages.success(request, "Skill was deleted!")
        return redirect('user-account')

    context = {'object': skill}
    return render(request, 'users/delete_skill.html', context)


@login_required(login_url="login")
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()

    context = {'messageRequests': messageRequests, 'unreadCount': unreadCount}

    return render(request, 'users/inbox.html', context)


@login_required(login_url="login")
def readMessage(request, pk):
    profile = request.user.profile
    messageRequest = profile.messages.get(id=pk)
    
    if messageRequest.is_read == False:
        messageRequest.is_read = True
        messageRequest.save()

    context = {'messageRequest': messageRequest}

    return render(request, 'users/message.html', context)


def sendMessage(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                message = form.save(commit=False)
                profile = request.user.profile
                message.sender = profile
                message.name = profile.name
                message.email = profile.email
                message.recipient = recipient
                message.save()
                messages.success(request, "Message was sent!")
                return redirect('user-profile', pk)
            else:
                message = form.save(commit=False)
                message.recipient = recipient
                message.save()
                messages.success(request, "Message was sent!")
                return redirect('user-profile', pk)

    context = {'recipient': recipient, 'form': form}

    return render(request, 'users/message_form.html', context)