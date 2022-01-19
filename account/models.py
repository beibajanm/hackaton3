from django.db import models

# Create your models here.
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self,email,password,**extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.create_activation_code()
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=50,blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return self.email

    def create_activation_code(self):
        import hashlib
        string = self.email + str(self.id)
        encode_string = string.encode()
        md5_object = hashlib.md5(encode_string)
        activation_code = md5_object.hexdigest()
        self.activation_code = activation_code


    def create_activation_coder(self):
        from django.utils.crypto import get_random_string
        code = get_random_string(8, '1236549')
        self.activation_code = code
        self.save()

# Gender = (
#     ('female', 'female'),
#     ('male', 'male'),
#     ('other','other'),
# )


# class UserProfile(models.Model):
#     user = models.OneToOneField(MyUser, primary_key=True, related_name='profiles', on_delete=models.CASCADE)
#     name = models.CharField(max_length=100, blank=True, null=True)
#     gender = models.CharField(choices=Gender)
#     date_of_birth = models.DateField(null=True, blank=True)
#     avatar = models.ImageField(upload_to='profile_pics', blank=True, null=True)
#     bio = models.CharField(max_length=250, blank=True, null=True)