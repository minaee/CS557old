from pyexpat import model
from django.db import models
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator


class Classroom(models.Model):
    building = models.CharField(max_length=15, primary_key=True)
    room_number = models.CharField(max_length=7)
    capacity = models.IntegerField(null=True,
                                   blank=True,
                                   validators=[MaxLengthValidator(4, message="No more than 4 digits.")])
    
    # composite primary key implementation in django
    # it states that each building has only one class with a specific room number
    UniqueConstraint(fields=['building', 'room_number'], name="unique_classroom")
    # class Meta:
    #     unique_together = (("building", "room_number"),)
        

class Department(models.Model):
    dept_name = models.CharField(max_length=20, 
                                 null=False, 
                                 blank=False, 
                                 primary_key=True)
    building = models.CharField(max_length=15, primary_key=True)
    budget = models.FloatField(null=False,
                               blank=False, 
                               validators=[MaxLengthValidator(14, message="No more than 12 digits!"), 
                                           MinValueValidator(0.0, "Salary should be positive!")])
    

class course(models.Model):
	# (course_id		varchar(8), 
	#  title			varchar(50), 
	#  dept_name		varchar(20),
	#  credits		numeric(2,0) check (credits > 0),
	#  primary key (course_id),
	#  foreign key (dept_name) references department
	# 	on delete set null
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
    password = models.CharField(max_length = 10)
    name = models.CharField(max_length = 200)


class Instructor(Person):    
    
	#  salary			numeric(8,2) check (salary > 29000),
	#  primary key (ID),
	#  foreign key (dept_name) references department
	# 	on delete set null 
    salary = models.FloatField(null=False,
                               blank=False, 
                               validators=[MaxLengthValidator(8, message="No more than 8 digits!"), 
                                           MinValueValidator(29000.0, "Salary should be more than $29000!")])
    dept_name = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

