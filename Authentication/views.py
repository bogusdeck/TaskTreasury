import os
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import UserLoginForm, UserLogoutForm, UserSignupForm, TaskScreenshotForm
from .models import User, Task
from django.contrib.auth.hashers import make_password, check_password
from uuid import uuid4
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from assignment.forms import AdminTaskForm


def index(request):
    return redirect("/accounts/signin/")


def signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            fname = form.cleaned_data["fname"]
            lname = form.cleaned_data["lname"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user_to_create = User(
                fname=fname, lname=lname, email=email, password=password
            )
            user_to_create.save()
            print(user_to_create)
            print("account bn gaya")
            messages.success(request, "Account created successfully. please login")
            return redirect("/accounts/login/")  # change krna hai
    else:
        form = UserSignupForm()

    return render(request, "user/signup.html", {"form": form})


def signin(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.get(email=email)
            print(check_password(password, user.password))
            print(user)
            if user is not None and check_password(password, user.password):
                login(request, user)
                user.token = str(uuid4)
                print(user.token)
                user.save()
                if user.email == "admin@admin.com":
                    return redirect("/accounts/adminHome/")
                else:
                    return redirect("/accounts/profile/{}".format(user.email))
            else:
                print("nahi hua")
                messages.error(request, "Invalid email or password")
                return redirect("accounts/home/")
    else:
        form = UserLoginForm()

    return render(request, "user/login.html", {"form": form})


@login_required
def signout(request):
    if request.method == "POST":
        logout(request)
        return redirect("/accounts/login/")


@login_required
def profile(request, email):
    user = get_object_or_404(User, email=email)
    return render(request, "user/profile.html", {"user": user})


@login_required
def applist(request):
    tasks = Task.objects.all().order_by('id')
    paginator = Paginator(tasks, 5)

    page = request.GET.get("page")
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    return render(request, "user/applist.html", {"tasks": tasks})


@login_required
def points(request):
    return render(request, "user/points.html")


@login_required
def task(request):
    userTasks = request.user.tasks.all().order_by('id')
    paginator = Paginator(userTasks,5)
    pageNumber = request.GET.get('page')
    try:
        tasks = paginator.page(pageNumber)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    print(userTasks, "hoi hoi")
    return render(request, "user/doneTask.html", {"userTasks": tasks})


@admin_required
def adminaddApp(request):
    if request.method == "POST":
        form = AdminTaskForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            link = form.cleaned_data["link"]
            category = form.cleaned_data["category"]
            subcategory = form.cleaned_data["subcategory"]
            points = form.cleaned_data["points"]
            logo = form.cleaned_data["logo"]

            task = form.save(commit=False)
            task.save()
            # print(name, link, category, subcategory, points, logo)
            print("ureee rruurueureuureurue")

            if "logo" in request.FILES:
                logo_file = request.FILES["logo"]
                upload_path = os.path.join(settings.MEDIA_ROOT, "applogo")
                # os.makedirs(upload_path, exist_ok=True)
                fs = FileSystemStorage(location=upload_path)
                filename = fs.save(logo_file.name, logo_file)
                task.logo = os.path.join("applogo/", filename)
                print(task.logo)
                task.save()

            return redirect("/accounts/adminHome/")
    else:
        form = AdminTaskForm()

    return render(request, "admin/addApp.html", {"form": form})


@admin_required
def adminHome(request):
    tasks = Task.objects.all().order_by('id')
    paginator = Paginator(tasks, 5)

    page = request.GET.get("page")
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    return render(request, "admin/adminHome.html", {"tasks": tasks})


@admin_required
def deleteTask(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=task_id)
        task.delete()
    return redirect("adminHome")


@login_required
def taskDetails(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if task in request.user.tasks.all():
        return redirect("alreadyDone")

    if request.method == "POST":
        form = TaskScreenshotForm(request.POST, request.FILES)
        if form.is_valid():
            screenshot = form.cleaned_data["image"]
            upload_path = os.path.join(settings.MEDIA_ROOT, "screenshots")
            print(upload_path)
            fs = FileSystemStorage(location=upload_path)
            filename = fs.save(screenshot.name, screenshot)
            print(filename)
            print(screenshot.name)
            request.user.points += task.points 
            request.user.save()
            request.user.tasks.add(task)

        return redirect("task")
    else:
        form = TaskScreenshotForm()

    return render(request, "user/taskDetails.html", {"task": task, "form": form})

@login_required
def alreadyDone(request):
    return render(request, "user/alreadyDone.html")