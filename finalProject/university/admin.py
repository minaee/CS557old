from django.contrib import admin

from .models import *
# from django.contrib import admin

# Register your models here.
# usr = get_user_model()

admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Instructor)
admin.site.register(Section)
admin.site.register(Teaches)
admin.site.register(Takes)
admin.site.register(Advisor)
admin.site.register(Time_slot)
admin.site.register(Prereq)

class Classroom_Admin(admin.ModelAdmin):
    list_display = ('id', 'building', 'room_number', 'capacity' )
    list_display_links = ('building', 'room_number', 'capacity' )
    list_filter = ('building', 'room_number' )

    search_fields = ('building', 'room_number')

    list_per_page = 10
admin.site.register(Classroom, Classroom_Admin)


