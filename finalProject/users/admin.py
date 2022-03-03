from django.contrib import admin
from django.contrib.auth import get_user_model 
from .models import User  # ,  WishListItem, QuoteList
# from django.contrib import admin

# Register your models here.
# usr = get_user_model()

admin.site.register(User)

# class WishListItem_Admin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'owner', 'count', 'tag', 'when_is_required_date', 'submitted')
#     list_display_links = ('title', 'owner', 'count', 'tag', 'when_is_required_date', 'submitted')
#     list_filter = ('owner', 'tag', 'submitted')

#     search_fields = ('title', 'owner', 'tag')

#     list_per_page = 10
# admin.site.register(WishListItem, WishListItem_Admin)

# class QuoteList_Admin(admin.ModelAdmin):
#     list_display = ('id', 'owner', 'subject')
#     list_display_links = ('id', 'owner', 'subject')

#     search_fields = ( 'owner',)

#     list_per_page = 10
# admin.site.register(QuoteList, QuoteList_Admin)
