from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .manager import UserManager
import numpy as np
import datetime
import random
from django.utils.translation import gettext_lazy as _

class User(AbstractUser, PermissionsMixin):
    username = None
    first_name = models.CharField(_("first name"), max_length=30)
    last_name = models.CharField(_("last name"), max_length=30)
    email_id = models.EmailField(_("email id"),max_length=50)
    phone_number = models.IntegerField (_('phone_number'),unique=True,blank=True,null=True)
    Employee_id = models.CharField(_('employee id'),unique=True,max_length=9,default = random.randrange(10**8, 10**9))#createEmployeeId())
    Manager = models.BooleanField(_('are you a manager?'),default=False)
    Personal_leave = models.IntegerField(_('number of personal leave'),default=20)
    Medical_leave = models.IntegerField(_('number of medical leave'),default=20)
    USERNAME_FIELD = 'Employee_id'
    REQUIRED_FIELD = ["first_name", "last_name", "email_id"]
    
    object = UserManager()
    def createEmployeeId(self):
        id = random.randrange(10**8, 10**9)
        return id
    def is_manager(self):    
        return self.Manager   
    def __str__(self):
        return str(self.Employee_id)
                   
class Leave(models.Model):
    Employee_name = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE,related_name='employee')
    Start_date = models.DateField('start-date')
    End_date = models.DateField('end-date')
    No_of_Days = models.IntegerField('no-of-days',blank=True,null=True)
    Reason = models.TextField('reason',blank=True,null=True)
    Approved = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE,related_name='manager')
    #'approved',max_length=20
    LEAVE_CHOICES = (('Personal', 'Personal'),('Medical', 'Medical'),)
    Type = models.CharField(max_length=10,choices=LEAVE_CHOICES)
    STATUS_CHOICES = (('Pending', 'Pending'),('Approved', 'Approved'),('Rejected','Rejected'))
    Pending_Status = models.CharField(max_length=25,choices=STATUS_CHOICES,default="Pending",blank=True,null=True)
    
    def __str__(self):
      return self.Employee_name.first_name +' '+self.Employee_name.last_name+'-'+str(self.Start_date)+'-'+str(self.End_date)

    def save(self,*args,**kwargs):
        try:
            year,month,day = self.End_date.split("-")
            last_day = datetime.date(int(year),int(month),int(day)+1)
            days = np.busday_count(self.Start_date,last_day)
            self.No_of_Days=days
        except:
            pass
        super().save(*args,**kwargs)    
  

class Record(models.Model):
    Employee_name = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE)
    Date = models.DateField('date',default=datetime.date.today())
    Day = models.IntegerField('day',default=datetime.date.today().day)
    Month = models.IntegerField('month',default=datetime.date.today().month)
    Year = models.IntegerField('year',default=datetime.date.today().year)
    Access_time = models.TimeField('access-time',default=datetime.datetime.now())
    Logout_time = models.TimeField('logout-time',default=datetime.datetime.now())
    Modified_time = models.TimeField('modified-time',default=datetime.datetime.now())
    Time_worked = models.FloatField('time-worked',blank=True,null=True)

    def __str__(self):
        return str(self.Date)+'-'+self.Employee_name.first_name +' '+self.Employee_name.last_name
    
    def time_worked(self):
        try:
            time_hr = (self.Logout_time.hour-self.Modified_time.hour)+(self.Modified_time.hour-self.Access_time.hour)
            time_min = (self.Logout_time.minute-self.Modified_time.minute)+(self.Modified_time.minute-self.Access_time.minute)
            time_w = time_hr + (time_min/60)
            return time_w
        except:
            return 0
    def save(self,*args,**kwargs):
        self.Time_worked=self.time_worked()
        super().save(*args,**kwargs)    



    

