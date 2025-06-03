from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
from django.db import models
from django.utils import timezone
# from django.contrib.postgres.fields import ArrayField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class Task(models.Model):
    CATEGORY_CHOICES = [
        ("social networking", "Social Networking"),
        ("entertainment", "Entertainment"),
        ("utilities", "Utilities"),
        ("productivity", "Productivity"),
        ("health and fitness", "Health and Fitness"),
        ("finance", "Finance"),
        ("shopping", "Shopping"),
        ("news", "News"),
        ("lifestyle", "Lifestyle"),
    ]

    name = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=400)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    points = models.IntegerField()
    logo = models.ImageField()


    def save(self, *args, **kwargs):
        if self.category and self.subcategory:
            if self.subcategory not in Task.get_available_subcategories(self.category):
                raise ValueError("Invalid subcategory for the selected category")
        super().save(*args, **kwargs)

    @staticmethod
    def get_available_subcategories(category):
        subcategories = {
            "social networking": [
                "Messaging",
                "Social Media",
                "Dating",
                "Professional Networking",
            ],
            "entertainment": [
                "Video Streaming",
                "Music Streaming",
                "Gaming",
                "Live Streaming",
                "Ticket Booking",
            ],
            "utilities": [
                "Weather",
                "Calculator",
                "File Management",
                "Translation",
                "QR Code Scanner",
            ],
            "productivity": [
                "Note-taking",
                "Task Management",
                "Document Editing",
                "Calendar",
                "Email",
            ],
            "health and fitness": [
                "Diet Tracking",
                "Meditation",
                "Yoga",
                "Sleep Tracking",
            ],
            "finance": [
                "Banking",
                "Expense Tracking",
                "Investment",
                "Budgeting",
                "Tax Filing",
            ],
            "shopping": [
                "E-commerce",
                "Grocery Delivery",
                "Coupon and Deals",
                "Fashion",
                "Second-hand Goods",
            ],
            "news": [
                "General News",
                "Tech News",
                "Sports News",
                "Finance News",
                "Local News",
            ],
            "lifestyle": [
                "Food and Drink",
                "Home Decor",
                "Fashion and Beauty",
                "Dating",
                "Horoscopes",
            ],
        }
        return subcategories.get(category, [])

class User(AbstractBaseUser, PermissionsMixin):
    fname = models.CharField(max_length=50, null=False)
    lname = models.CharField(max_length=50, null=False)
    email = models.EmailField(max_length=50, null=False, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    ifLogged = models.BooleanField(default=False)
    token = models.CharField(max_length=500, null=True, default="")
    tasks = models.ManyToManyField(Task, related_name='users')
    # completedTask = ArrayField(models.IntegerField, default=list, black=True, verbose_name='completed task',help_task='IDS of Completed Tasks')
    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        related_name="user_set",
        related_query_name="user",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fname", "lname"]

    def __str__(self):
        return self.email