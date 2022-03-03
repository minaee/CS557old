from pyexpat import model
from statistics import mode
from time import time
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator

from datetime import datetime

class Classroom(models.Model):
    building = models.CharField(max_length=15)
    room_number = models.CharField(max_length=7)
    capacity = models.IntegerField(null=True,
                                   blank=True,
                                   validators=[MaxLengthValidator(4, message="No more than 4 digits.")])
    
    # # composite primary key implementation in django
    # # it states that each building has only one class with a specific room number
    # UniqueConstraint(fields=['building', 'room_number'], name="unique_classroom")
    # # class Meta:
    # #     unique_together = (("building", "room_number"),)
        

class Department(models.Model):
    dept_name = models.CharField(max_length=20, 
                                 null=False, 
                                 blank=False, 
                                 primary_key=True)
    building = models.CharField(max_length=15)
    budget = models.FloatField(null=False,
                               blank=False, 
                               validators=[MaxLengthValidator(14, message="No more than 12 digits!"), 
                                           MinValueValidator(0.0, "Salary should be positive!")])
    

class Course(models.Model):
    course_id = models.CharField(max_length=8,
                                 primary_key=True)
    title = models.CharField(max_length=50)
    dept_name = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    credits = models.IntegerField(null=False, 
                                   blank=False, 
                                   validators=[MinValueValidator(0, message="Credits should be positive values."),
                                               MinLengthValidator(0, message="Credits should be only 2 digits."),
                                               MaxLengthValidator(0, message="Credits should be only 2 digits.")])
  
  
class Person(models.Model):
    first_name = models.CharField(max_length = 25)
    last_name = models.CharField(max_length = 25)
    # dept_name = models.CharField(max_length = 25)
    
    class Meta:
        abstract = True
    
    def __str__(self) -> str:
        return str(self.first_name) + " " + str(self.last_name)


class Student(Person): 
    tot_cred = models.IntegerField(null=False, 
                                   blank=False, 
                                   validators=[MinValueValidator(0, message="Credits should be positive values.")])
    
    dept_name = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )


class Instructor(Person): 
    salary = models.FloatField(null=False,
                               blank=False, 
                               validators=[MaxLengthValidator(8, message="No more than 8 digits!"), 
                                           MinValueValidator(29000.0, "Salary should be more than $29000!")])
    dept_name = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )


class Section(models.Model):
    course_id = models.ForeignKey(Course, 
                                  on_delete=models.CASCADE)
    sec_id = models.CharField(max_length=8)
    seasons = (
        ("Fall", "Fall"),
        ("Winter", "Winter"),
        ("Spring", "Spring"),
        ("Summer", "Summer")
    )
    semester = models.CharField(max_length=6, choices=seasons)
    year = models.DateField(validators=[MinValueValidator(datetime(1701, 1, 1, 0, 0, 0)),
                                        MaxValueValidator(datetime(2100, 1, 1, 0, 0, 0))])
    building = models.ForeignKey(Classroom,
                                 on_delete=models.CASCADE,
                                 related_name="SectionBuilding")
    room_number = models.ForeignKey(Classroom,
                                    on_delete=models.CASCADE,
                                    related_name="SectionRoomNumber")
    time_slot_id = models.CharField(max_length=4)
    
    # # composite primary key implementation in django
    # UniqueConstraint(fields=['course_id', 'sec_id', 'semester', 'year'], name="unique_section")



class Teaches(models.Model):
    id = models.OneToOneField(Instructor,
                           on_delete=models.CASCADE,
                           primary_key=True,
                           related_name="TeachesId",
                           unique=True)
    course_id = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="TeachesCourseId")
    sec_id = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="TeachesSectionId")
    semester = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="teachesSemester")
    year = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="TeachesYaer")
    # # composite primary key implementation in django
    # UniqueConstraint(fields=['id', 'course_id', 'sec_id', 'semester', 'year'], name="unique_teaches")    


class Takes(models.Model):
    id = models.OneToOneField(Student,
                           on_delete=models.CASCADE,
                           primary_key=True,
                           unique=True)
    course_id = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="TakesCourseId")
    sec_id = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="TakesSectionId")
    semester = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="TakesSemester")
    year = models.ForeignKey(Section, 
                                  on_delete=models.CASCADE,
                                  related_name="TakesYear")
    # # composite primary key implementation in django
    # UniqueConstraint(fields=['id', 'course_id', 'sec_id', 'semester', 'year'], name="unique_teaches")


class Advisor(models.Model):
    s_id = models.ForeignKey(Student,
                             on_delete=models.CASCADE)
    i_id = models.ForeignKey(Instructor,
                             on_delete=models.CASCADE)


class Time_slot(models.Model):
    time_slot_id = models.CharField(max_length=4)
    week_days = (
        ("sa", "Saturday"),
        ("su", "Sunday"),
        ("mo", "Monday"),
        ("tu", "Tuseday"),
        ("we", "Wednesday"),
        ("th", "Thursday"),
        ("fr", "Friday")
    )
    day = models.CharField(max_length=9, null=False, blank=False, choices=week_days)
    start_hr = models.TimeField(null=False, blank=False)
    # start_min = 
    end_hr = models.TimeField(null=False, blank=False)
    # end_min = 


class Prereq(models.Model):
    course_id = models.ForeignKey(Course, 
                                  on_delete=models.CASCADE,
                                  related_name="Current")
    prereq_id = models.ForeignKey(Course, 
                                  on_delete=models.CASCADE,
                                  related_name="Prereq")
