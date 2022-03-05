from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import (PasswordChangeView, PasswordChangeDoneView, 
                                        PasswordResetView, PasswordResetDoneView,
                                        PasswordResetConfirmView, PasswordResetCompleteView)

from . import views

# handler404 = 'cms.views.my_custom_page_not_found_view'
# handler500 = 'cms.views.my_custom_error_view'
# handler403 = 'cms.views.my_custom_permission_denied_view'
# handler400 = 'cms.views.my_custom_bad_request_view'

urlpatterns = [
    path('signup/', views.signUpView, name='signup'),
    path('signup/student/', views.studentSignUpView, name='student_signup'),
    path('signup/instructor/', views.instructorSignUpView, name='instructor_signup'),



    path('login', views.mylogin, name='log_in'),
    path('register', views.register, name='register'),
    path('log_out', views.mylogout, name='log_out'),
    path('dashboard', views.dashboard, name='dashboard'),
    
    path('user_inbox', views.user_inbox, name='user_inbox'),
    path('admin_inbox', views.admin_inbox, name='admin_inbox'),
    # path('admin_inbox/<str:contact_chat_id>', views.chat, name='chat'),
    re_path(r'^admin_inbox/chat=(?P<contact_sender_id>([A-Z]*)([0-9]*){11})/$', views.chat, name='chat'),
    re_path(r'^user_inbox/(?P<message_id>([A-Z]*)([0-9]*){11})/$', views.message_view, name='message_view'),
    
    re_path(r'^reply/message=(?P<message_id>([A-Z]*)([0-9]*){19})/$', views.answer_message, name='answer_message'),
    
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('change_password', views.change_password, name='change_password'),
    path('password_reset_sent', views.password_reset_sent, name='password_reset_sent'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="users/password/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password/password_reset_complete.html'), name='password_reset_complete'),  
    path("password_reset", views.password_reset_request, name="password_reset"),

    path('my_products', views.my_products, name='my_products'),
    path('submit_quote', views.submit_quote, name='submit_quote'),
    path('received_quotes', views.received_quotes, name='received_quotes'),
    re_path(r'^received_quotes/quote_list_user(?P<user_id>([A-Z]*)([0-9]*){11})/$', views.quote_list, name='quote_list'),
    re_path(r'^received_quotes/quote=(?P<quote_id>([A-Z]*)([0-9]*){19})/$', views.quote_details, name='quote_details'),
    re_path(r'^quote_history/quote=(?P<quote_id>([A-Z]*)([0-9]*){19})/$', views.quote_history, name='quote_history'),

    path('get_products', views.get_products, name='get_products' ),
    
]