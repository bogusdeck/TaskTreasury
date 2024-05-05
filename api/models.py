from django.db import models
from Authentication.models  import User

# class User(models.Model):
#     fname = models.CharField(max_length=50,null=False)
#     lname = models.CharField(max_length=50,null=False) 
#     email = models.EmailField(max_length=50, null=False)
#     password =  models.CharField(max_length=50)
#     ifLogged = models.BooleanField(default=False)
#     token = models.CharField(max_length=500, null=True, default="")

#     def __str__(self):
#         return "{} -{}".format(self.fname,self.lname)
    