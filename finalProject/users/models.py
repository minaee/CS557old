from __future__ import unicode_literals

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxLengthValidator

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    
    first_name = models.CharField(_('first name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, null=True, blank=True)
    
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_promoted = models.BooleanField(_('Is Promoted'), default=False, help_text="To promote the user for special features, e.g. univeristy staff & ...")

    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    
    email = models.EmailField(_('email address'), unique=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_user(self):
        return self

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        firstname = self.first_name.lstrip()
        firstname = firstname.rstrip()
        lastname = self.last_name.lstrip()
        lastname = lastname.rstrip()
        full_name = str(firstname) + ' ' + str(lastname)
        return full_name
        
    def get_info(self):
        info = ('Name: ' + str(self.get_full_name()) + ',\n'
                'Email: ' + str(self.email) )
        return info
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tot_cred = models.IntegerField(null=False, 
                                   blank=False, 
                                   validators=[MinValueValidator(0, message="Credits should be positive values.")])
    
    dept_name = models.ForeignKey(
        'university.Department',
        on_delete=models.CASCADE
    )


class Instructor(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    salary = models.FloatField(null=False,
                               blank=False, 
                               validators=[MaxLengthValidator(8, message="No more than 8 digits!"), 
                                           MinValueValidator(29000.0, "Salary should be more than $29000!")])
    
    dept_name = models.ForeignKey(
        'university.Department',
        on_delete=models.CASCADE
    )