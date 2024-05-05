from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from .views import signout, signin, signup, profile, index, applist, points, task, adminaddApp, adminHome, taskDetails, deleteTask, alreadyDone
urlpatterns = [
    path("", index, name="index"),
    path("login/", signin, name="signin"),
    path("signup/", signup, name="signup"),
    path("signout/", signout, name="signout"),
    path("profile/<str:email>/", profile, name="profile"),
    path("applist/", applist, name="applist"),
    path("points/", points, name="points"),
    path("task/", task, name="task"),
    path("adminaddApp/",adminaddApp, name="adminaddApp"),
    path("adminHome/",adminHome, name="adminHome"),
    path("deleteTask/<int:task_id>/",deleteTask, name="deleteTask"),
    path("task/<int:task_id>/",taskDetails, name="taskDetails"),
    path("alreadyDone/", alreadyDone , name ="alreadyDone")
] 



# admin id : admin@admin.com
# admin password : admin 

