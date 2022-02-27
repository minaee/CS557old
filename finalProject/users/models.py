from __future__ import unicode_literals

from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    
    

    first_name = models.CharField(_('first name'), max_length=30, null=True, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, null=True, blank=True)
    
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=True)
    is_promoted = models.BooleanField(_('Is Promoted'), default=False, help_text="To promote the user for special features, e.g. SmartFlow Demo & ...")


    company = models.CharField(_('company'), default='', max_length=50, null=True, blank=True)  #  (max_length=50, null=True, blank=True)

    address = models.TextField(max_length=500, null=True, blank=True)
    zipcode = models.CharField(max_length=12, 
                                  null=True, blank=True, error_messages ={ 
                                  "max_length":"Zipcodes are not more than 12 characters."
                                  },
                                  validators=[RegexValidator(r'^[0-9]{5,12}$')])

    city = models.CharField(max_length=25, null=True, blank=True)
    country = models.CharField(max_length=25, null=True, blank=True)

    tel = models.CharField(_('phone'), max_length=17, null=True, blank=True)
    mobile = models.CharField(_('mobile'), max_length=17, null=True, blank=True)

    fax = models.CharField(max_length=17, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)

    user_id = models.CharField(max_length=14, unique=True, null=True, blank=True)
    title = models.CharField(max_length=10, null=True, blank=True)

    
    website = models.CharField(_('website'), max_length=50, null=True, blank=True)

    previous_visit = models.DateTimeField(null=True, blank=True)
    current_visit = models.DateTimeField(null=True, blank=True)
    
    
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # class MPTTMeta:
    #     order_insertion_by = ['email']

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

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)
        
    def get_info(self):
        info = ('Name: ' + str(self.get_full_name()) + ',\n'
                'Email: ' + str(self.email) + ',\n'
                'Address: ' + str(self.address + ', ' + self.city + ', ' +  self.country + ', ' +  self.zipcode) + ',\n' 
                'Mobile: ' + str(self.mobile))
        return info
