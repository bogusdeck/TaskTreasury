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
from main.forms import AdminTaskForm


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
            
            # Check if user with this email already exists
            try:
                existing_user = User.objects.get(email=email)
                messages.error(request, "An account with this email already exists")
                return render(request, "user/signup.html", {"form": form})
            except User.DoesNotExist:
                # Create new user
                try:
                    user_to_create = User(
                        fname=fname, lname=lname, email=email, password=password
                    )
                    user_to_create.save()
                    print("Account created successfully")
                    messages.success(request, "Account created successfully. Please login")
                    return redirect("/accounts/login/")
                except Exception as e:
                    print(f"Error creating account: {str(e)}")
                    messages.error(request, f"Error creating account: {str(e)}")
                    return render(request, "user/signup.html", {"form": form})
        else:
            # Form is invalid, errors will be shown via toastr
            print("Form errors:", form.errors)
            return render(request, "user/signup.html", {"form": form})
    else:
        form = UserSignupForm()

    return render(request, "user/signup.html", {"form": form})


def signin(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
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
                    print("Invalid password")
                    messages.error(request, "Invalid password")
                    return render(request, "user/login.html", {"form": form})
            except User.DoesNotExist:
                print("User not found")
                messages.error(request, "No account found with this email")
                return render(request, "user/login.html", {"form": form})
        else:
            # Form is invalid, errors will be shown via toastr
            print("Form errors:", form.errors)
            return render(request, "user/login.html", {"form": form})
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
        print("POST request received")
        print("FILES:", request.FILES)
        print("POST data:", request.POST)
        
        form = TaskScreenshotForm(request.POST, request.FILES)
        print("Form is valid:", form.is_valid())
        
        if not form.is_valid():
            print("Form errors:", form.errors)
        
        if form.is_valid():
            screenshot = form.cleaned_data["image"]
            print("Screenshot received:", screenshot)
            
            # Create screenshots directory if it doesn't exist
            upload_path = os.path.join(settings.MEDIA_ROOT, "screenshots")
            os.makedirs(upload_path, exist_ok=True)
            
            print("Upload path:", upload_path)
            fs = FileSystemStorage(location=upload_path)
            filename = fs.save(screenshot.name, screenshot)
            print("Saved filename:", filename)
            
            # Add points and mark task as completed
            request.user.points += task.points 
            request.user.save()
            request.user.tasks.add(task)
            print("Task marked as completed, points added:", task.points)
            
            return redirect("task")
        else:
            # Re-render the form with errors
            return render(request, "user/taskDetails.html", {"task": task, "form": form, "error": "Please upload a valid image file."})
    else:
        form = TaskScreenshotForm()

    return render(request, "user/taskDetails.html", {"task": task, "form": form})

@login_required
def alreadyDone(request):
    return render(request, "user/alreadyDone.html")