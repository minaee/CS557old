from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, get_object_or_404

from django.views import generic
from django.views.generic import View
from django.contrib.auth.forms import UserChangeForm
from django.urls import reverse_lazy

from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMultiAlternatives
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from itertools import chain

from university.models import Student


from .models import User, Student, Instructor
from .choices import country_choices, generate_code


from datetime import datetime, date
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django import forms

import json
import urllib
import urllib.request
from django.conf import settings
from django.contrib import messages

from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

import logging

from django.utils.timezone import now

# from .models import Profile
import re

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def index(request):
    return render(request, 'users/index.html')
    

def studentSignUpView(request):
    """
        student signup view
    """
    context = {
        # 'country_choices': country_choices
    }

    if request.method == 'POST':
        # Get form values

        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        email = request.POST['email']
        
        tot_cred = request.POST['tot_cred']
        dept_name = request.POST['dept_name']
        
        
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if password match
        if password == password2:
            # Check email
            
            User = get_user_model()
            # Check Email
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is being used.')
                return redirect('student_signup', context)
            else:
                user = User.objects.create_user(
                                            password=password,
                                            email=email,
                                            first_name=first_name,
                                            last_name=last_name,
                                            is_promoted=False,
                                            is_student=True,
                                            is_instructor=False)
                user.save()
                
                student = Student.objects.create(
                    user=user,
                    tot_cred=tot_cred,
                    dept_name=dept_name
                )
                student.save()
                
                return redirect('log_in')
                
        else:
            messages.error(request, 'Passwords doesnt match!')
            return redirect('student_signup', context)
    else:
        return render(request, 'users/student_signup.html', context)


def instructorSignUpView(request):
    """
        instructor signup view
    """
    context = {
        # 'country_choices': country_choices
    }

    if request.method == 'POST':
        # Get form values

        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        email = request.POST['email']
        
        salary = request.POST['salary']
        dept_name = request.POST['dept_name']
        
        
        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if password match
        if password == password2:
            # Check email
            
            User = get_user_model()
            # Check Email
            if User.objects.filter(email=email).exists():
                messages.error(request, 'That email is being used.')
                return redirect('instructor_signup', context)
            else:
                user = User.objects.create_user(
                                            password=password,
                                            email=email,
                                            first_name=first_name,
                                            last_name=last_name,
                                            is_promoted=False,
                                            is_student=False,
                                            is_instructor=True)
                user.save()
                
                instructor = Instructor.objects.create(
                    user=user,
                    salary=salary,
                    dept_name=dept_name
                )
                instructor.save()
                
                return redirect('log_in')
                
        else:
            messages.error(request, 'Passwords doesnt match!')
            return redirect('instructor_signup', context)
    else:
        return render(request, 'users/instructor_signup.html', context)


def signUpView(request):
    return render(request, 'users/login.html')
    
    
def register(request):
    logger = logging.getLogger(__name__)

    context = {
        # 'country_choices': country_choices
    }

    if request.method == 'POST':
        # Get form values

        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        email = request.POST['email']

        password = request.POST['password']
        password2 = request.POST['password2']

        # Check if password match
        if password == password2:
            # Check email
            
            User = get_user_model()
            # Check Email
            if User.objects.filter(email=email).exists():
                logger.error('Something went wrong!')
                messages.error(request, 'That email is being used.')
                return redirect('register', context)
            else:
                user = User.objects.create_user(
                                            password=password,
                                            email=email,
                                            first_name=first_name,
                                            last_name=last_name,
                                            is_promoted=False)
                user.save()
                return redirect('log_in')
                
        else:
            messages.error(request, 'Passwords doesnt match!')
            return redirect('register', context)
    else:
        return render(request, 'users/register.html', context)
    
   
def mylogin(request):
    logger = logging.getLogger(__name__)
    if request.method == 'POST':
        
        username = request.POST['username']
        password = request.POST['password']

        # remember_me = request.POST.get('remember_me')
        # print('\n\n\nRemember me: %s\n\n\n'%remember_me)
        
        ''' Begin reCAPTCHA validation '''
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY_LOGIN,
                'response': recaptcha_response
            }
        data = urllib.parse.urlencode(values).encode()
        req =  urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())
        ''' End reCAPTCHA validation '''

        if result['success']:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                if True:  # not remember_me: # if remember me is not selected
                    request.session.set_expiry(0)  
                    request.session.modified = True

                user.previous_visit = user.current_visit                
                user.current_visit = datetime.now()
                user.save(update_fields=['previous_visit', 'current_visit'])
                
                messages.success(request, 'You are now logged in')
                # return redirect('dashboard')
                return redirect('my_products')
                # return render(request, 'users/my_products.html')
            else:
                logger.error('Something went wrong!')
                messages.error(request, 'Invalid credentials.')
                # return redirect('log_in')
                return render(request, 'users/login.html')
        else:
            messages.error(request, 'Invalid reCAPTCHA. Please try again.')
            # return redirect('log_in')
            return render(request, 'users/login.html')
        
    else:
        return render(request, 'users/login.html')


def mylogout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('index')
    else:
        # pass
        messages.error(request, 'Unknown error!!!')
        return redirect('index')

@login_required
def dashboard(request):
    # user_contacts = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)

    
    context = {
        # 'contacts': user_contacts
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def user_inbox(request):
    today = datetime.now
    # user_contacts = Contact.objects.order_by('-contact_date').filter(sender_id=request.user.user_id)  # receiver_id=request.user.user_id)
    # user_contacts_2 = Contact.objects.order_by('-contact_date').filter(receiver_id=request.user.user_id)
    # user_contacts = Contact.objects.filter(Q(sender_id=request.user.user_id)|Q(in_converstation=False)).order_by('-contact_date')
    # user_contacts = Contact.objects.filter(owner=request.user, in_converstation=False).order_by('-contact_date')
    
    current_user = request.user
    admin_list = User.objects.filter(is_superuser__icontains=True)
    admin_emails = []
    for u in admin_list:
        admin_emails.append(u.email)
   
    # result_list = list(chain(user_contacts, user_contacts_2))

    # pagintor = Paginator(user_contacts, 5)
    # page = request.GET.get('page')
    # paged_user_contacts = pagintor.get_page(page)

    context = {
        # 'products_choices': products_choices,
        # 'services_choices': services_choices,
        # 'support_choices': support_choices,
        # 'company_choices': company_choices,
        # 'country_choices': country_choices,
        # 'contacts': paged_user_contacts
    }

    # if request.method == 'POST' and 'delete_message_from_user_inbox_button' in request.POST:
    #     message_id = request.POST['message_id']
    #     sender_id = request.POST.get('sender_id')  
    #     receiver_id = request.POST['receiver_id']
    #     chat_id = request.POST['chat_id']

        
    #     try:
    #         this_message = Contact.objects.get(message_id=message_id, 
    #                                            sender_id=sender_id, 
    #                                            receiver_id=receiver_id,
    #                                            chat_id=chat_id)
    #         this_message.delete()
    #         replies_to_this_message = Contact.objects.filter(Q(in_converstation=True), Q(chat_id=chat_id))
    #         for item in replies_to_this_message:
    #             item.delete()
    #         # go = SomeModel.objects.get(foo='bar')
    #     except ObjectDoesNotExist:
    #         this_message = None
    #     print('this message: ', this_message.message)
        
    #     return redirect('user_inbox')

    return render(request, 'users/user_inbox.html', context)

@login_required
def message_view(request, message_id):

    # # user_contacts = Contact.objects.filter(message_id=message_id)
    # base_message = Contact.objects.get(message_id=message_id)
    # base_message.is_opened_user = True
    # base_message.save()
    
    # # replies = Contact.objects.filter(chat_id=base_message.owner.id)
    # replies = Contact.objects.filter(chat_id=base_message.message_id, in_converstation=True).order_by('contact_date')
    # # print('replies: ', replies)
    # # print('base_message.owner.id: ', base_message.owner.id)
    # for item in replies:
    #     item.is_opened_user = True
    #     item.save()
        
    # pagintor = Paginator(replies, 3)
    # page = request.GET.get('page')
    # paged_replies = pagintor.get_page(page)

    context = {
        # 'message_id': message_id,
        # 'contact': base_message,
        # 'general': general,
        # 'replies': paged_replies
    }        
    return render(request, 'users/message.html', context)

@login_required
def admin_inbox(request):

    # user_contacts = Contact.objects.distinct('sender_id')  # .latest()

    # user_contacts = Contact.objects.distinct('sender_id').select_related()
    # user_contacts = Contact.objects.filter(in_converstation=False).order_by('-contact_date')
    # users_info = User.objects.all()
    
    # if request.method == 'POST' and 'delete_message_from_admin_inbox_button' in request.POST:
    #     id = request.POST['id']
    #     sender_id = request.POST.get('sender_id')  
    #     receiver_id = request.POST['receiver_id']
    #     chat_id = request.POST['chat_id']

        
    #     try:
    #         this_message = Contact.objects.get(id=id, 
    #                                            sender_id=sender_id, 
    #                                            receiver_id=receiver_id,
    #                                            chat_id=chat_id)
    #         this_message.delete()
    #         replies_to_this_message = Contact.objects.filter(Q(in_converstation=True), Q(chat_id=id))
    #         for item in replies_to_this_message:
    #             item.delete()
    #         # go = SomeModel.objects.get(foo='bar')
    #     except ObjectDoesNotExist:
    #         this_message = None
    #     print('this message: ', this_message.message)
        
    #     return redirect('admin_inbox')

    # pagintor = Paginator(user_contacts, 5)
    # page = request.GET.get('page')
    # paged_user_contacts = pagintor.get_page(page)

    context = {
        # 'products_choices': products_choices,
        # 'services_choices': services_choices,
        # 'support_choices': support_choices,
        # 'company_choices': company_choices,
        # 'country_choices': country_choices,
        # 'status_choices': status_choices,
        # 'contacts': paged_user_contacts
    }

    return render(request, 'users/admin_inbox.html', context)

@login_required
def answer_message(request, message_id):

    # # message_to_answer = Contact.objects.filter(message_id__icontains=message_id)
    # message_to_answer = Contact.objects.get(message_id=message_id)
    # message_to_answer.status = Contact.Choices_status.processing
    # message_to_answer.is_opened_admin = True
    # message_to_answer.save()
    
    
    # replies = Contact.objects.filter(chat_id=message_to_answer.message_id, in_converstation=True).order_by('contact_date')
    # for item in replies:
    #     # if not item.owner.is_superuser:
    #     item.is_opened_admin = True
    #     item.save()
    
    # if request.method == 'POST' and 'delete_message_from_user_inbox_button' in request.POST:
    #     message_id = request.POST['message_id']
    #     sender_id = request.POST.get('sender_id')  
    #     receiver_id = request.POST['receiver_id']
    #     chat_id = request.POST['chat_id']

        
    #     try:
    #         this_message = Contact.objects.get(message_id=message_id, 
    #                                            sender_id=sender_id, 
    #                                            receiver_id=receiver_id,
    #                                            chat_id=chat_id)
    #         this_message.delete()
    #         # go = SomeModel.objects.get(foo='bar')
    #     except ObjectDoesNotExist:
    #         this_message = None
    #     print('this message: ', this_message.message)
        
    #     return redirect('user_inbox')
    
    context = {
        # 'this_message': message_to_answer,
        # 'products_choices': products_choices,
        # 'services_choices': services_choices,
        # 'support_choices': support_choices,
        # 'company_choices': company_choices,
        # 'country_choices': country_choices,
        # 'general': general,
        # 'replies': replies
    }

    
    
    return render(request, 'users/answer_message.html', context)

@login_required
def chat(request, contact_sender_id):

    # user_contacts = Contact.objects.order_by('-contact_date').filter(sender_id=contact_sender_id)

    # pagintor = Paginator(user_contacts, 6)
    # page = request.GET.get('page')
    # paged_user_contacts = pagintor.get_page(page)    

    context = {
        # 'contact_sender_id': contact_sender_id,
        # 'contacts': paged_user_contacts
    }
    
    # if request.method == 'POST':
    #     status = request.POST['status']
    #     message_id = request.POST.get('message_id')  
        
    #     this_message = Contact.objects.order_by('-contact_date').filter(sender_id=contact_sender_id, message_id=message_id)
    #     print('this_message.message: ', this_message.message)
    #     if this_message:
    #         this_message = Contact(status=status)
    #         this_message.save()
        
    #     return render('chat', contact_sender_id)

    
    # if request.method == 'POST' :
    #     status = request.POST['status']
    #     print('status:             ', status)
    #     message_id = request.POST.get('message_id')
    #     list = get_object_or_404 ( Contact, message_id=message_id)
    #     list.status = request.POST.get('status')
    #     list.save()

    return render(request, 'users/chat.html', context)

@login_required
def edit_profile(request):
    
    context = {
        'country_choices': country_choices
    }

    if request.method == 'POST':
        # Get form values
        title = request.POST.get('title')

        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')

        company = request.POST.get('company')
        address = request.POST.get('address')

        zipcode = request.POST.get('zipcode')
        city = request.POST.get('city')

        country = request.POST['country']
        
        website = request.POST.get('website')

        tel = request.POST.get('tel')
        mobile = request.POST.get('mobile')

        fax = request.POST.get('fax')

        # username = request.POST.get('username')
        email = request.POST.get('email')

        # Check if password match
        User = get_user_model()
        
        me = request.user

        request.user.title = title
        request.user.first_name = first_name
        request.user.last_name = last_name

        me.company = company
        request.user.address = address

        me.zipcode = zipcode
        me.city = city
        me.country = country
        me.website = website
        me.tel = tel
        me.mobile = mobile
        me.fax = fax
        me.email = email

        me.save()
        # User.save()

        # user = User.objects. create_user(
        #                                     email=email,
        #                                     first_name=first_name,
        #                                     last_name=last_name,
        #                                     title=title,
        #                                     company=company,
        #                                     address=address,
        #                                     zipcode=zipcode,
        #                                     city=city,
        #                                     country=country,
        #                                     website=website,
        #                                     phone=phoneNumber,
        #                                     fax=fax)
                                                    
                    
                    

        #                     # # Login after register
        #                     # # auth.login(request, user)
        #                     # # messages.success(request, 'You are now logged in')
        #                     # # return redirect('index')

        # user.save()
        # update_profile(request, user.id, company, address, zipcode, city, country, phoneNumber)

        
        messages.success(request, 'your profile has changed.')
        return redirect('edit_profile')
            
            
    else:
        return render(request, 'users/edit_profile.html', context)

@login_required    
def change_password(request):

    current_user = request.user

    if request.method == 'POST':

        email = request.POST['email']
        # password2 = request.POST['password2']


        update_session_auth_hash(request, current_user)  # Important!
        # messages.success(request, 'We\'ve emailed you instructions for setting your password. You should receive the email shortly!')
        return redirect('password_reset_sent')

    else:
        return render(request, 'users/change_password.html')
    
@login_required    
def password_reset_sent(request):
    return render(request, 'users/password_reset_sent.html')

@login_required
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "users/password/password_reset_email.txt"
                    c = {
                        "email":user.email,
                        'domain':'127.0.0.1:8000',
                        'site_name': 'Alternativ',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                        }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'hw.fbuser@gmail.com' , [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect ("password_reset_done")
            
    password_reset_form = PasswordResetForm()
    context = {
        "password_reset_form": password_reset_form
        }
    return render(request, 'users/password/password_reset.html', context)


# from products.models import (Intro_products, Ip_sensor, Smartflow,
#                              Water_quality_sensor, Accessories)
# from services.models import (Autmotive, Avionics, Digital_transformation,
#                              Healthcare, Precise_farming, Railway)
# from support.models import  Training_Lists


# from .models import  WishListItem, QuoteList

from django.core import serializers
from django.template.loader import render_to_string
from itertools import chain

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# from requests import request
from django.utils import timezone
# from contacts.list_of_topics import products_choices, services_choices, support_choices, company_choices, general
# from .models.QuoteList.Choices_status import sent, processing, 

@login_required
def my_products(request):
    
    # ip_sensor = Ip_sensor.objects.filter(is_published=True).order_by('title').only('id', 'title', 'cover')
    # smartflow = Smartflow.objects.filter(is_published=True).order_by('title').only('id', 'title', 'picture')
    # water_quality_sensor = Water_quality_sensor.objects.filter(is_published=True).order_by('title').only('id', 'title', 'picture')
    # accesories = Accessories.objects.all().filter(is_published=True).order_by('title').only('id', 'title', 'cover')
    
    # automotive = Autmotive.objects.all().order_by('title').only('id', 'title')
    # avionics = Avionics.objects.all().order_by('title').only('id', 'title')
    # digital_transformation = Digital_transformation.objects.all().order_by('title').only('id', 'title')
    # healthcare = Healthcare.objects.all().order_by('title').only('id', 'title')
    # precise_farming = Precise_farming.objects.all().order_by('title').only('id', 'title')
    # railway = Railway.objects.all().order_by('title').only('id', 'title')
    
    # today = datetime.today()
    # datem = datetime(today.year, 1, 1)
    
    # webinars = Seminars.objects.filter(presentation_date__gte=datem).order_by('title')
    # tranings = Training_Lists.objects.all().order_by('title')
    
    # wishlistitem = WishListItem.objects.filter(owner=request.user).order_by('tag')
    
    # wishlistitem_with_price = WishListItem.objects.filter(owner=request.user, category_name__icontains="Support").order_by('tag')
    # # print('\n\nwith price: ', wishlistitem_with_price)
    # wishlistitem_without_price = WishListItem.objects.filter(Q(owner=request.user), ~Q(category_name__icontains="Support")).order_by('-add_to_list_date')
    # # print('\n\nwithout price: ', wishlistitem_without_price)
    
    # queries_products = chain(ip_sensor, 
    #                     smartflow, 
    #                     water_quality_sensor, 
    #                     accesories,)
    # products_js = list(chain(ip_sensor, 
    #                     smartflow, 
    #                     water_quality_sensor, 
    #                     accesories,))
    # queries_services = chain(automotive, 
    #                         avionics, 
    #                         digital_transformation, 
    #                         healthcare,
    #                         precise_farming,
    #                         railway)
    
    # queries = chain(ip_sensor, 
    #                 smartflow, 
    #                 water_quality_sensor, 
    #                 accesories,
    #                 automotive, 
    #                 avionics, 
    #                 digital_transformation, 
    #                 healthcare,
    #                 precise_farming,
    #                 railway,
    #                 # webinars,
    #                 tranings
    #                 )
    
    
    # class_types = {}
    # for item in queries:
    #     if item.type() not in class_types.keys():
    #         class_types[item.type()] = ContentType.objects.get_for_model(item)
    #         # print("\ninja itemeeeeeeeee: ", item)
        
    # # print('class_types: ', class_types)
    # # for query in list(queries):
    # #         if len(query) > 0:    
    # #             for item in query:
    # #                 # if item['type']
    # #                 # print('request.POST.get(item): ', request.POST.get(item))
    # #                 print('item type: ', item['type'])

    # # if request.method == 'POST':
    # if request.method=='POST' and 'add_to_wishlist_button' in request.POST:
    # # if 'add_to_wishlist_button' in request.POST:
    #     owner = request.user
        
    #     title_type = request.POST.getlist('title_type')
    #     # print('\ntitle_type: \n', title_type)
        
    #     for item in request.POST.getlist('title_type'):
    #         object_id = request.POST.get('item_id_%s'%item)
    #         tag = request.POST.get('tag_%s'%item)
            
    #         category_name = request.POST.get('category_%s'%item)
    #         class_name = request.POST.get('class_%s'%item)
    #         if request.POST.get('price_%s'%item) == "0":
    #             price = 0
    #         else:
    #             price = float(request.POST.get('price_%s'%item))
    #         # print('\ntag: ', tag )
    #         # print('\nclass_types[tag]: ', class_types[tag])
    #         # print('request.POST.get("check_%s"%item): ', request.POST.get('check_%s'%item, None), item)
    #         # if category_name is 'Services' request.POST.get('check_%s'%item, None) is 'on':
    #         if category_name != 'Services':
    #             # print('heere: ', item, 'categry name is : ', category_name)
    #             count = request.POST.get('count_%s'%item)
    #         else:
    #             if request.POST.get('check_%s'%item, None) == 'on':
    #                 # print('%s is on'%item)
    #                 count = '1'
    #             else:
    #                 count = '0'
    #         title = request.POST.get('title_%s'%item)
    #         if count != '0':
                
    #             obj, created = WishListItem.objects.get_or_create(
    #                 owner=owner,
    #                 content_type=class_types[tag],
    #                 object_id=object_id,
    #                 tag=tag,
    #                 category_name=category_name,
    #                 class_name=class_name,
    #                 title=title,
    #                 submitted=False,
    #             )
    #             if not created:
    #                 print('here is the new item: ', obj, created)
    #                 fee= float(obj.price / obj.count)
                    
    #                 obj.count = obj.count + int(count)
    #                 obj.price = price * obj.count
    #                 obj.add_to_list_date = datetime.now()
    #                 obj.save(update_fields=['count', 'price', 'add_to_list_date'])
    #             else:
    #                 obj.count = int(count)
    #                 obj.price = price * int(count)
    #                 obj.add_to_list_date = datetime.now()
    #                 obj.save(update_fields=['count', 'price', 'add_to_list_date'])
                
    #             # try:
    #             #     this_item = WishListItem.objects.get(title=title, tag=tag)
    #             #     this_item.count = this_item.count + int(count)
    #             #     this_item.save(update_fields=['count',])
    #             # except WishListItem.DoesNotExist:
    #             #     this_item = WishListItem(owner=owner,
    #             #                     content_type=class_types[tag],
    #             #                     object_id=object_id,
    #             #                     tag=tag,
    #             #                     category_name=category_name,
    #             #                     class_name=class_name,
    #             #                     price=price,
    #             #                     count=count,
    #             #                     title=title)
    #             #     this_item.save()

                
    #             # if this_item:
    #             #     print('\nthis item: ', this_item)
    #             #     # print('\nthis item count: ', this_item.count)
    #             #     # print('this item type: ', type(this_item.count))
    #             #     # print('input count type: ', type(int(count)))
    #             #     this_item.count = this_item.count + int(count)
    #             #     this_item.save(update_fields=['count',])
    #             # else:
    #             #     print('\nno shit found!!!\n')
                    
    #             #     wishlist = WishListItem(owner=owner,
    #             #                     content_type=class_types[tag],
    #             #                     object_id=object_id,
    #             #                     tag=tag,
    #             #                     category_name=category_name,
    #             #                     class_name=class_name,
    #             #                     price=price,
    #             #                     count=count,
    #             #                     title=title)
    #             #     wishlist.save()
        
    #     return redirect('my_products')
    
    # elif request.method=='POST' and 'delete_from_wishlist_button' in request.POST:
        
    #     unique_id = request.POST.getlist('unique_id')
    #     # print('\ntag_id: \n', unique_id)
        
    #     for item in request.POST.getlist('unique_id'):
    #         # item_id = request.POST.get('item_id_%s'%item)
    #         # print('id: ', item_id)
    #         # item = get_object_or_404(WishListItem, pk=item_id)
    #         item_id = int(request.POST.get('item_id_%s'%item))  
    #         item_title = request.POST.get('item_title_%s'%item)
    #         item_tag = request.POST.get('item_tag_%s'%item)
    #         print("\n\nrequest.POST.get('count_%s'%item):", request.POST.get('count_%s'%item), item)
    #         item_count = int(request.POST.get('item_count_%s'%item))
    #         # start_date = request.POST.get('start_date_%s'%item)
    #         # print('\n\n\nstart_date: ', start_date)
    #         # date = datetime.strptime(str(start_date) ,"%Y-%m-%d")
    #         # print('\n\n\n entered date: ', date )
    #         # print('date.today(): ', date.today())
    #         # object = ContentType.objects.get(app_label='users', model='user')
    #         # object.get_object_for_this_type(username='Guido')

    #         item = WishListItem.objects.get(id=item_id, title=item_title, tag=item_tag) 
    #         # item, created = WishListItem.objects.get_or_create(id=item_id, title=item_title, tag=item_tag, submitted=False)
            
    #         if item_count == 0:
    #             print('item to delete: ', item, item_count) 
    #             item.delete()
    #         elif item_count > 0:   
    #             print('item to change: ', item, item_count) 
                
    #             fee= float(item.price / item.count)
                
    #             item.count = item_count
    #             item.price = fee * item_count
    #             item.add_to_list_date = timezone.now()
                
    #             # if date < date.today():
    #             #     messages.error(request, "The entered date should be greater than today's date.")
    #             #     return redirect('my_products')
    #             # else:
    #             #     item.when_is_required_date = date
    #             #     item.save(update_fields=['count', 'price', 'add_to_list_date', 'when_is_required_date'])
    #             item.save(update_fields=['count', 'price', 'add_to_list_date'])


    #     # item.delete()
        
    #     return redirect('my_products')
    
    # elif request.method=='POST' and 'delete_service_from_wishlist_button' in request.POST:
    #     unique_id = request.POST.getlist('unique_id')
    #     # print('\ntag_id: \n', unique_id)
        
    #     for item in request.POST.getlist('unique_id'):
    #         # item_id = request.POST.get('item_id_%s'%item)
    #         # print('id: ', item_id)
    #         # item = get_object_or_404(WishListItem, pk=item_id)
    #         item_id = int(request.POST.get('item_id_%s'%item))  
    #         item_title = request.POST.get('item_title_%s'%item)
    #         item_tag = request.POST.get('item_tag_%s'%item)
    #         print("\n\nrequest.POST.get('count_%s'%item):", request.POST.get('count_%s'%item), item)
    #         # item_count = int(request.POST.get('item_count_%s'%item))
    #         # start_date = request.POST.get('start_date_%s'%item)
    #         # print('\n\n\nstart_date: ', start_date)
    #         # date = datetime.strptime(str(start_date) ,"%Y-%m-%d")
    #         # print('\n\n\n entered date: ', date )
    #         # print('date.today(): ', date.today())
    #         item = WishListItem.objects.get(id=item_id, title=item_title, tag=item_tag) 
            
    #         print('item to delete: ', item) 
    #         item.delete()
                
    #     return redirect('my_products')
        
    
    # paginator = Paginator(wishlistitem, 8)  
    # page = request.GET.get('page')
    # paged_queries = paginator.get_page(page)
    
    # products_js = serializers.serialize('json', products_js)

    context = {
        
        # 'ip_sensor': ip_sensor,
        # 'smartflow': smartflow,
        # 'water_quality_sensor': water_quality_sensor,
        # 'accesories': accesories,
        
        # 'automotive': automotive,
        # 'avionics': avionics,
        # 'digital_transformation': digital_transformation,
        # 'healthcare': healthcare,
        # 'precise_farming': precise_farming,
        # 'railway': railway,
        
        # 'queries_products': queries_products,
        # 'queries_services': queries_services,
        # # 'webinars': webinars,
        # 'tranings': tranings,
        
        
        # 'products_js': products_js,
        # # 'wishes': wishes,
        # # 'wishes_items': wishes_items,
        # 'wishlistitem': paged_queries,
        # 'wishlistitem_with_price': wishlistitem_with_price,
        # 'wishlistitem_without_price': wishlistitem_without_price,
        
    }
    return render(request, 'users/basket/my_products.html', context)

@login_required
def submit_quote(request):

    # wishlistitem = WishListItem.objects.filter(Q(owner=request.user), Q(submitted=False), ~Q(category_name__icontains='Support') ).order_by('tag')
    
    
    # if request.method=='POST':
    #     owner = request.user
        
    #     subject = request.POST.get('subject') 
    #     message = request.POST['message']
        
    #     if 'attached_file' in request.FILES:
    #         attached_file = request.FILES['attached_file']
    #     else:
    #         attached_file = ""
        
    #     wish_item = []
    #     unique_id = request.POST.getlist('unique_id')
    #     print('unique id: ', unique_id)
    #     for item in request.POST.getlist('unique_id'):
    #         item_id = int(request.POST.get('item_id_%s'%item))  
    #         item_title = request.POST.get('item_title_%s'%item)
    #         item_tag = request.POST.get('item_tag_%s'%item)
            
    #         when_is_required_date = request.POST.get('when_is_required_date_%s'%item)
    #         print('\n\nwhen_is_required_date: ', when_is_required_date)
    #         entered_date = datetime.strptime(str(when_is_required_date) ,"%Y-%m-%d")
    #         entered_date = date(entered_date.year, entered_date.month, entered_date.day)
    #         print('entered entered_date: ', entered_date )
            
    #         if not (entered_date > date.today()):
                
    #             messages.error(request, "The entered date should be greater than today's date.")
    #             return redirect('submit_quote')
    #         else:
    #             temp_wish_item = WishListItem.objects.get(id=item_id, title=item_title, tag=item_tag)
    #             temp_wish_item.when_is_required_date = entered_date
    #             temp_wish_item.save(update_fields=['when_is_required_date',])
                
    #             wish_item.append(temp_wish_item )
    #             print('wish_item: ', wish_item)
                
    #     quote = QuoteList(owner=owner)
    #     quote.save()
    #     for temp_item in wish_item:
    #         temp_item.quoteList = quote
    #         temp_item.save()
            
    #     for temp_item in wish_item:
    #         temp_item.submitted = True
    #         temp_item.save(update_fields=['submitted', ])
        
    #     # quote.owner=owner
    #     quote.subject=subject
    #     quote.message=message
    #     quote.attached_file=attached_file
    #     quote.creation_date=datetime.now()
    #     quote.user_id=owner.id
    #     quote.status = QuoteList.Choices_status.submitted
    #     quote.converstation_id = quote.id
    #     quote.in_converstation = False
    #     quote.is_opened_user = True
    #     quote.is_opened_admin = False
    #     quote.save(update_fields=['subject', 'message', 'attached_file', 'creation_date', 
    #                                 'user_id', 'converstation_id', 'in_converstation',
    #                                 'is_opened_user', 'is_opened_admin' ])
        
    #     messages.success(request,  "Your request has been submitted, \
    #                                 we will get back to you soon.")
        
    #     admin_list = User.objects.filter(is_superuser__icontains=True)
    #     admin_emails = []
    #     for u in admin_list:
    #         admin_emails.append(u.email)
    #     wishlistitem = WishListItem.objects.filter(owner=quote.owner, quoteList=quote, )
    #     # print('\nName: ', quote.owner.get_full_name())
    #     # print('item in wish list:\n')
    #     customer_name = quote.owner.get_full_name()
    #     if quote.owner.title:
    #         customer_name = quote.owner.title + ' ' + customer_name
    #     email_message = ''
    #     for item in wishlistitem:
    #         # print('> ', item)
    #         email_message = email_message + str(item.count) + ' x ' + item.title + ' from ' + item.class_name + ' in ' + item.category_name + '<br>'
    #     # print('email_message: ', email_message)

    #     # send_mail(
    #     #         'New Quote from ' + customer_name,
    #     #         (customer_name + ' has submitted a quote request containing following items:\n'
    #     #         + email_message +
    #     #         '\n\nSign into the dashboard for more info.\n'),
    #     #         'hw.fbuser@gmail.com', # system@alternativeng.com
    #     #         admin_emails,
    #     #         fail_silently=False)
        
    #     email_body = cleanhtml(message)
    #     subject_email = 'New Quote from ' + customer_name
    #     from_email = 'system@alternativeng.com'
    #     to = admin_emails
    #     text_content = ('\n"\n' + email_body + '"\n')
    #     html_content = ('<p>' + customer_name + ' has submitted a quote request containing following items:</p>'
    #                     '<p>' + email_message + '</p>'
    #                     '<p>Sign into the <a href="https://alternativeng.com/users/login">dashboard</a> for more info.</p>')
                        
    #     msg = EmailMultiAlternatives(subject_email, text_content, from_email, to)
    #     msg.attach_alternative(html_content, "text/html")
    #     msg.send()

            
        
    #     return redirect('my_products')
                
    context = {
        # 'products_choices': products_choices,
        # 'services_choices': services_choices,
        # 'support_choices': support_choices,
        # 'company_choices': company_choices,
        # 'country_choices': country_choices,
        # 'general': general,
        # 'wishlistitem': wishlistitem,
        # 'today':  date.today(),
    }

    return render(request, 'users/basket/submit_quote.html', context)

@login_required
def received_quotes(request):

    # user_contacts = Contact.objects.distinct('sender_id')  # .latest()

    # user_quotes = QuoteList.objects.distinct('owner').order_by('owner', '-creation_date').select_related()
    # user_quotes = QuoteList.objects.filter(Q(in_converstation=False)).order_by('-creation_date')
    # users_info = User.objects.all()
    
    # wish_items = []
    # for item in user_quotes:
    #     first_item = WishListItem.objects.filter(Q(owner=item.owner), Q(submitted=True), Q(quoteList=item)).order_by('tag')
    #     # print('\nfirst item in wish list', first_item, item)
    #     # listed = list(first_item)
    #     # print('listed', listed[0])
    #     # for it in listed:
    #     #     print('type: ', type(it), ' and: ', it)
    #     latest_answer_owner = QuoteList.objects.filter(Q(converstation_id=item.id)).order_by('-creation_date').first()
    #     replies_for_item = QuoteList.objects.filter(Q(converstation_id=item.id)).order_by('-creation_date')
    #     has_unread = False
    #     for reply in replies_for_item:
    #         if reply.is_opened_admin == False:
    #             has_unread = True
                
    #     # print('latest_answer_owner: ', latest_answer_owner)
    #     # print('latest_answer_owner type: ', type(latest_answer_owner))
    #     wish_items.append(
    #         {'quote': item, 'wish_item': first_item, 'latest_answer_owner': latest_answer_owner, 'has_unread': has_unread,}
    #     )
    # print('wish_items: ', wish_items)
    # # for item in wish_items:
    # #     print('0: ', item[0])
    # #     print('1: ', item[1])

    # print(user_contacts.query)
    # if request.method == 'POST' and 'delete_quote_from_received_quotes_button' in request.POST:
    #     quote_id = request.POST['quote_id']
    #     # sender_id = request.POST.get('sender_id')  
    #     # receiver_id = request.POST['receiver_id']
    #     # chat_id = request.POST['chat_id']

        
    #     try:
    #         this_quote = QuoteList.objects.get(id=quote_id)
    #         this_quote.delete()
            
    #         # print('mssages to delete: ')
    #         replies_to_delete = QuoteList.objects.filter(Q(converstation_id=quote_id), Q(in_converstation=True))
    #         # replies = QuoteList.objects.filter(Q(converstation_id=quote_id), Q(in_converstation=True)).order_by('creation_date')
    #         # for msg in replies_to_delete:
    #             # print('msg: ', msg.message)
    #         # print('items to delete: ')
    #         for item in replies_to_delete:
    #             # print('items: ', item)
    #             item.delete()
            
            
            
    #         # go = SomeModel.objects.get(foo='bar')
    #     except ObjectDoesNotExist:
    #         this_quote = None
    #     print('this quote: ', this_quote.owner)
        
    #     return redirect('received_quotes')

    # pagintor = Paginator(user_quotes, 5)
    # page = request.GET.get('page')
    # paged_user_quotes = pagintor.get_page(page)

    context = {
        # 'products_choices': products_choices,
        # 'services_choices': services_choices,
        # 'support_choices': support_choices,
        # 'company_choices': company_choices,
        # 'country_choices': country_choices,
        # 'status_choices': status_choices,
        # 'user_quotes': paged_user_quotes,
        # 'wish_items': wish_items,
    }

    return render(request, 'users/basket/received_quotes.html', context)

@login_required
def quote_list(request, user_id):

    # user_quotes = QuoteList.objects.order_by('-creation_date').filter(user_id=user_id)

    # pagintor = Paginator(user_quotes, 3)
    # page = request.GET.get('page')
    # paged_user_quotes = pagintor.get_page(page)    

    context = {
        # 'contact_sender_id': contact_sender_id,
        # 'quotes': paged_user_quotes
    }
    
    # if request.method == 'POST':
    #     status = request.POST['status']
    #     message_id = request.POST.get('message_id')  
        
    #     this_message = Contact.objects.order_by('-contact_date').filter(sender_id=contact_sender_id, message_id=message_id)
    #     print('this_message.message: ', this_message.message)
    #     if this_message:
    #         this_message = Contact(status=status)
    #         this_message.save()
        
    #     return render('chat', contact_sender_id)

    
    # if request.method == 'POST' :
    #     status = request.POST['status']
    #     print('status:             ', status)
    #     message_id = request.POST.get('message_id')
    #     list = get_object_or_404 ( Contact, message_id=message_id)
    #     list.status = request.POST.get('status')
    #     list.save()

    return render(request, 'users/basket/quote_list.html', context)

@login_required
def quote_details(request, quote_id):

    # # quote = QuoteList.objects.filter(id=quote_id)
    # base_quote = get_object_or_404(QuoteList, id=quote_id)
    # if base_quote.status is QuoteList.Choices_status.submitted:
    #     base_quote.status = QuoteList.Choices_status.processing
    #     base_quote.save()
    
    # base_quote.is_opened_admin = True
    # base_quote.status = QuoteList.Choices_status.processing
    # base_quote.save(update_fields=['is_opened_admin', 'status', ])
    # # print('\n\n\n\nquote message:', quote.message)
    # # wishlistitem = WishListItem.objects.filter(owner=quote.owner, submitted=True, )
    # wishlistitem = WishListItem.objects.filter(Q(owner=base_quote.owner), Q(submitted=True), Q(quoteList=base_quote)).order_by('tag')
    # # print('\nName: ', quote.owner.get_full_name())
    # # print('item in wish list:\n')
    # # for item in wishlistitem:
    # #     print('> ', item)
    # # if quote.attached_file:
    # #     print('name: ', quote.attached_file.name)
    # #     name = quote.attached_file.name.split("/")[-1]
    # #     print('name: ', quote.get_file_name() )
    # replies = QuoteList.objects.filter(Q(converstation_id=quote_id), Q(in_converstation=True)).order_by('creation_date')
    # for item in replies:
    #     item.is_opened_admin = True
    #     item.save(update_fields=['is_opened_admin'])
    
    # if request.method=='POST':
    #     owner_id = request.POST.get('owner_id')
    #     print('owner_id: ', owner_id)
    #     owner = get_object_or_404(User, id=owner_id)
    #     print('owner: ', owner)
        
        
    #     converstation_id = request.POST.get('converstation_id') 
    #     in_converstation = request.POST.get('in_converstation') 
    #     subject = request.POST.get('subject') 
    #     message = request.POST['message']
        
    #     if 'attached_file' in request.FILES:
    #         attached_file = request.FILES['attached_file']
    #     else:
    #         attached_file = ""
        
        
        
    #     # quote = QuoteList(owner=owner)
    #     # quote.save()
        
    #     # Saving reply to quote
    #     quote = QuoteList(owner=owner,
    #                       message=message,
    #                       attached_file=attached_file,
    #                       creation_date=datetime.now(),
    #                       converstation_id=converstation_id,
    #                       in_converstation=in_converstation,
    #                       user_id=owner.id,
    #                       status = QuoteList.Choices_status.ready,
    #                       is_opened_admin=True,
    #                       is_opened_user=False)
    #     quote.save()
        
    #     # Changing the status of quote to ready so that user knows about new msg
    #     base_quote.status = QuoteList.Choices_status.ready
    #     base_quote.save()
        
    #     messages.success(request,  "Your reply has been submitted.")
        
    #     # admin_list = User.objects.filter(is_superuser__icontains=True)
    #     # admin_emails = []
    #     # for u in admin_list:
    #     #     admin_emails.append(u.email)
    #     # wishlistitem = WishListItem.objects.filter(owner=quote.owner, quoteList=quote, )
    #     # # print('\nName: ', quote.owner.get_full_name())
    #     # # print('item in wish list:\n')
    #     # email_message = ''
    #     # for item in wishlistitem:
    #     #     # print('> ', item)
    #     #     email_message = email_message + '\n' + str(item.count) + ' of ' + item.title + ' from ' + item.class_name + ' in ' + item.category_name
    #     # # print('email_message: ', email_message)

    #     # send_mail(
    #     #         'New Quote from website',
    #     #         (quote.owner.get_full_name() + 'has submitted a quote request containing following items:\n'
    #     #         + email_message +
    #     #         '\n\nSign into the dashboard for more info.\n'),
    #     #         'system@alternativeng.com',
    #     #         admin_emails,
    #     #         fail_silently=False)
        
    #     send_email_to = base_quote.owner.email
    #     receiver_name = base_quote.owner.get_full_name()
    #     # print('receiver name', receiver_name)
        
    #     if base_quote.owner.title:
    #         receiver_title = base_quote.owner.title
    #         receiver_name = str(receiver_title + ' ' + receiver_name)
    #         # print('receiver name with title', receiver_name)
        
    #     # send_mail(
    #     #     'Quote from Alternativ engineering',
    #     #     ('Dear ' + receiver_name + ',\n\n'
    #     #     'you have a message in your inbox, Please Sign in into your dashboard for more information.\n\n'
    #     #     'Best reagrds\n'
    #     #     'Alternativ Engineering A-Z GmbH\n'
    #     #     'Sautterweg  5/ Nr.49 | 70565 Stuttgart | Deutschland\n'
    #     #     'Registereintrag.: HRB 775292\n'
    #     #     'USt-IdNr.: DE335948882\n'
    #     #     'Telefon: +49 711 30039660\n'
    #     #     'Mobil: +49 176 83532344\n'
    #     #     'E-Mail: sales@AlternativEng.com\n'
    #     #     'Web: https://www.AlternativEng.com'),
    #     #     'hw.fbuser@gmail.com',  # 'sales@alternativeng.com',
    #     #     [send_email_to],
    #     #     fail_silently=False)
    #     email_body = cleanhtml(message)
    #     subject_email = 'Quote from Alternativ engineering'
    #     from_email = 'sales@alternativeng.com'
    #     to = send_email_to
    #     text_content = ('\n"\n' + email_body + '"\n')
    #     html_content = ('<p>Dear ' + receiver_name + ',</p>'
    #                     '<p>you have a message in your inbox, Please Sign in into your <a href="https://alternativeng.com/users/login">dashboard</a> for more information.<br>'
    #                     'Best reagrds</p>'
    #                     '<p>Alternativ Engineering A-Z GmbH<br>'
    #                     'Sautterweg  5/ Nr.49 | 70565 Stuttgart | Deutschland<br>'
    #                     'Registereintrag.: HRB 775292<br>'
    #                     'USt-IdNr.: DE335948882<br>'
    #                     'Telefon: +49 711 30039660<br>'
    #                     'Mobil: +49 176 83532344<br>'
    #                     'E-Mail: sales@AlternativEng.com<br>'
    #                     'Web: https://www.AlternativEng.com</p>')
                        
    #     msg = EmailMultiAlternatives(subject_email, text_content, from_email, [to])
    #     msg.attach_alternative(html_content, "text/html")
    #     msg.send()
                
    context = {
        # 'quote': base_quote,
        # 'wishlistitem': wishlistitem,
        # 'replies': replies,
        # 'products_choices': products_choices,
        # 'services_choices': services_choices,
        # 'support_choices': support_choices,
        # 'company_choices': company_choices,
        # 'country_choices': country_choices,
        # 'general': general
    }

    
    
    return render(request, 'users/basket/quote_details.html', context)

@login_required
def quote_history(request, quote_id):
    
    # base_quote = get_object_or_404(QuoteList, id=quote_id)
    # user_quotes = QuoteList.objects.filter(Q(converstation_id=base_quote.id), Q(in_converstation=True)).order_by('creation_date')
    # for item in user_quotes:
    #     item.is_opened_user = True
    #     item.save(update_fields=['is_opened_user'])
    # wishlistitem = WishListItem.objects.filter(Q(owner=base_quote.owner), Q(submitted=True), Q(quoteList=base_quote)).order_by('tag')
    
    # if request.method=='POST':
    #     owner_id = request.POST.get('owner_id')
    #     # print('owner_id: ', owner_id)
    #     owner = get_object_or_404(User, id=owner_id)
    #     # print('owner: ', owner)
        
        
    #     converstation_id = request.POST.get('converstation_id') 
    #     in_converstation = request.POST.get('in_converstation') 
    #     subject = request.POST.get('subject') 
    #     message = request.POST['message']
        
    #     if 'attached_file' in request.FILES:
    #         attached_file = request.FILES['attached_file']
    #     else:
    #         attached_file = ""
        
        
        
    #     # quote = QuoteList(owner=owner)
    #     # quote.save()
        
        
    #     quote = QuoteList(owner=owner,
    #                       message=message,
    #                       attached_file=attached_file,
    #                       creation_date=datetime.now(),
    #                       converstation_id=converstation_id,
    #                       in_converstation=in_converstation,
    #                       user_id=owner.id,
    #                       status = QuoteList.Choices_status.submitted,
    #                       is_opened_user=True,
    #                       is_opened_admin=False)
    #     quote.save()
        
    #     # changing quote status to ready and waiting for an admin to reply it
    #     base_quote.status = QuoteList.Choices_status.submitted
    #     base_quote.save()
        
    #     messages.success(request,  "Your request has been submitted, \
    #                                 we will get back to you soon.")
        
    #     admin_list = User.objects.filter(is_superuser__icontains=True)
    #     admin_emails = []
    #     for u in admin_list:
    #         admin_emails.append(u.email)
    #     wishlistitem = WishListItem.objects.filter(owner=base_quote.owner, quoteList=base_quote, )
    #     # print('\nName: ', quote.owner.get_full_name())
    #     # print('item in wish list:\n')
    #     customer_name = quote.owner.get_full_name()
    #     if quote.owner.title:
    #         customer_name = quote.owner.title + ' ' + customer_name
    #     email_message = ''
    #     for item in wishlistitem:
    #         # print('> ', item)
    #         email_message = email_message + str(item.count) + ' x ' + item.title + ' from ' + item.class_name + ' in ' + item.category_name + '<br>'
    #     # print('email_message: ', email_message)
    #     message_body = cleanhtml(message)
    #     # send_mail(
    #     #         'New Quote from ' + customer_name,
    #     #         (customer_name + ' has submitted a reply to quote request containing following items:\n'
    #     #         + email_message + '\n' 
    #     #         'Message body: \n"\n'
    #     #          + message_body + '\n"\n'
    #     #         '\n\nSign into the dashboard for more info.\n'),
    #     #         'hw.fbuser@gmail.com', # system@alternativeng.com
    #     #         admin_emails,
    #     #         fail_silently=False)
    #     email_body = cleanhtml(message)
    #     subject_email = 'New Quote from ' + customer_name
    #     from_email = 'system@alternativeng.com'
    #     to = admin_emails
    #     text_content = ('\n"\n' + email_body + '"\n')
    #     html_content = ('<p>' + customer_name + ' has submitted a reply to quote request containing following items:</p>'
    #                     '<p>' + email_message + '</p>' 
    #                     '<p>Message body: <br>"<br>'
    #                         + message_body + '<br>"</p>'
    #                     '<p>Sign into the <a href="https://alternativeng.com/users/login">dashboard</a> for more info.</p>')
                        
    #     msg = EmailMultiAlternatives(subject_email, text_content, from_email, to)
    #     msg.attach_alternative(html_content, "text/html")
    #     msg.send()
        
        
    context = {
        # 'quote': base_quote,
        # 'wishlistitem': wishlistitem,
        # 'replies': user_quotes,
        # 'products_choices': products_choices,
        # 'services_choices': services_choices,
        # 'support_choices': support_choices,
        # 'company_choices': company_choices,
        # 'country_choices': country_choices,
        # 'general': general
    }

    
    
    return render(request, 'users/basket/quote_history.html', context)
    
def get_products(request):
    # queryset_list_intro_products = Intro_products.objects.all().order_by('title') 
    # queryset_list_ip_sensor = Ip_sensor.objects.all()  
    # queryset_list = ControlValves.objects.all()  
    # queryset_list_water_quality_sensor = Water_quality_sensor.objects.all()  
    
    # products = 0 

    # if request.method == 'POST':
    #     products_checkbox = request.POST.get('products')

    #     if products_checkbox:
    #         products = serializers.serialize('json', list(queryset_list_intro_products))

    #         # products = queryset_list_intro_products.to_json(orient='records')           
        
    #     context = {
    #         'products': products,
    #     }
    #     # return render(request, 'users/basket/my_products.html', context)
    #     return JsonResponse(context, status=200)

    context = {
        # 'intro_products': queryset_list_intro_products,
        
    }
    return null  # render(request, 'users/basket/my_products.html') # , context)