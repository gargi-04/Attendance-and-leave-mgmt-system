from django.shortcuts import render,redirect,HttpResponse
import calendar
from django.http import HttpResponseRedirect
from calendar import HTMLCalendar
#from datetime import datetime
import datetime
from .models import *
from .models import User
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
import numpy as np
from calendar import monthrange

# Create your views here.
@login_required(login_url='/login')
def home(request):
    return redirect("/dashboard/")

@login_required(login_url='/login')
def decision(request,leaveId,status):
    approval = Leave.objects.all().filter(id=leaveId).first()
    if status:
        if approval.Type=="Medical":
            approval.Employee_name.Medical_leave-=approval.No_of_Days
        elif approval.Type=="Personal":
            approval.Employee_name.Personal_leave-=approval.No_of_Days
        approval.Employee_name.save()        
        approval.Pending_Status="Approved"
    elif status==0:
        approval.Pending_Status="Rejected"
    approval.Approved = request.user    
    approval.save()  
    return redirect('/approval/')   

@login_required(login_url='/login')
def approval(request):
    approvals = Leave.objects.all().filter(Pending_Status="Pending").order_by('-Start_date')
    return render(request,"approval.html",{'approvals':approvals})

def calculatePercentage(user,month,year):
    monthRecord = Record.objects.all().filter(Employee_name=user,Month=month,Year=year)
    startdate = datetime.date(year,month,1)
    enddate = datetime.date.today()
    leaveRecord = Leave.objects.all().filter(Employee_name=user,Start_date__range=[startdate,enddate],Pending_Status="Approved") 
    medicalRecord = leaveRecord.filter(Type="Medical",Pending_Status="Approved")
    PersonalRecord = leaveRecord.filter(Type="Personal",Pending_Status="Approved")
    medical=0
    personal=0
    for i in medicalRecord:
        if i.End_date<=datetime.date.today():
            medical+=i.No_of_Days
        else:
            last_day = datetime.date(int(year),int(month),datetime.date.today().day+1)
            days = np.busday_count(i.Start_date,last_day)
            medical+=days
    for i in PersonalRecord:
        if i.End_date<=datetime.date.today():
            personal+=i.No_of_Days
        else:
            last_day = datetime.date(int(year),int(month),datetime.date.today().day+1)
            days = np.busday_count(i.Start_date,last_day)
            personal+=days
    present=monthRecord.__len__()
    last_day = None
    if year != datetime.date.today().year:
        last_day = datetime.date(year,month,monthrange(year,month)[1])
    elif month != datetime.date.today().month:
        last_day = datetime.date(year,month,monthrange(year,month)[1])
    else:
        last_day = datetime.date(int(year),int(month),datetime.date.today().day+1)
    saturdayCount=np.busday_count(startdate,last_day,weekmask='Sat')
    sundayCount=np.busday_count(startdate,last_day,weekmask='Sun')
    if last_day.strftime("%a")=="Sat":
        saturdayCount+=1
    elif last_day.strftime("%a")=="Sun":
        sundayCount+=1     
    Holiday = saturdayCount+sundayCount
    absent=datetime.date.today().day - medical - personal - present - Holiday
    return (medical,personal,present,absent,Holiday)
    
def calculateHours(user,month,year,day=datetime.date.today().day):
    monthRecord = Record.objects.all().filter(Employee_name=user,Month=month,Year=year)
    totalHour = 0
    averageHour = 0
    day = monthrange(year,month)[1]
    startdate = datetime.date(year,month,1)
    enddate = datetime.date(year,month,day)
    startweek = int(startdate.strftime("%U"))
    endweek = int(enddate.strftime("%U"))
    weeks = [x for x in range(startweek,endweek+1)]
    weekHour = [0 for x in range(startweek,endweek+1)]
    for hr in monthRecord:
        totalHour+=hr.Time_worked
        curr = int(hr.Date.strftime("%U"))
        currIndex = weeks.index(curr)
        weekHour[currIndex]+=hr.Time_worked
    medical,personal,present,absent,Holiday=calculatePercentage(user,datetime.date.today().month,datetime.date.today().year)
    averageHour = round(totalHour/(present+absent),2)
    totalHour = round(totalHour,2)
    return (totalHour,averageHour,weekHour)    

def getCalendar(user,month,year): 
    monthRecord = Record.objects.all().filter(Employee_name=user,Month=month,Year=year)
    startdate = datetime.date(year,month,1)
    day = monthrange(year,month)[1]
    enddate = datetime.date(year,month,day)
    leaveRecord = Leave.objects.all().filter(Employee_name=user,Start_date__range=[startdate,enddate],Pending_Status="Approved")
    presentDays = [x.Date.day for x in monthRecord]
    leaveDays = []
    print(leaveRecord)
    for i in leaveRecord:
        if i.End_date.month != datetime.date.today().month:
            lastday = monthrange(year, month)[1]
        else:  
            lastday = i.End_date.day
        for j in range(i.Start_date.day,lastday+1):
            leaveDays.append(j)
    cal = calendar.monthcalendar(year, month)
    for i in cal:
        for index,j in enumerate(i):
            if j in presentDays and year==datetime.date.today().year:
                i[index]=[j,"Present"]
            elif j in leaveDays and year==datetime.date.today().year:
                i[index]=[j,"Leave"]
            elif j in range(1,datetime.date.today().day+1) and year==datetime.date.today().year and month==datetime.date.today().month:
                i[index]=[j,"Absent"]
            else:
                i[index]=[j,""] 
    monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    monthName = monthNames[month-1]                   
    return (cal,leaveDays,presentDays,monthName,year)

@login_required(login_url='/login')
def dashboard(request):
    totalH,averH,weekHour = calculateHours(request.user,datetime.date.today().month,datetime.date.today().year)
    medical,personal,present,absent,Holiday=calculatePercentage(request.user,datetime.date.today().month,datetime.date.today().year)
    cal,leaveDays,presentDays,monthName,year = getCalendar(request.user,datetime.date.today().month,datetime.date.today().year)
    return render(request,"dashboard.html",locals(),)


def find_leaves(user):
    return Leave.objects.filter(Employee_name=user).order_by('-Start_date')
    
@login_required(login_url='/login')
def history(request):
    if request.user.is_authenticated:
        leaves = find_leaves(request.user)
        return render(request,"history.html",{'leaves':leaves})
    return HttpResponse(request,"Not Found")

@login_required(login_url='/login')
def seekEmployeeRecord(request,Employee_id,year = datetime.date.today().year, month =datetime.date.today().month):
    try:
        users = User.objects.all().filter(Manager=False).order_by('-Employee_id')
        currentUser = users.filter(Employee_id=Employee_id).first()
        totalH,averH,weekHour = calculateHours(currentUser,month,year)
        medical,personal,present,absent,Holiday=calculatePercentage(currentUser,month,year)
        leaves = find_leaves(currentUser)
        cal,leaveDays,presentDays,monthName,year = getCalendar(currentUser,month,year)
        return render(request,"record.html",locals())
    except:
        return redirect("/record/")

@login_required(login_url='/login')
def record(request):
    users = User.objects.all().filter(Manager=False).order_by('-Employee_id')
    currentUser = users.first()
    totalH,averH,weekHour = calculateHours(currentUser,datetime.date.today().month,datetime.date.today().year)
    medical,personal,present,absent,Holiday=calculatePercentage(currentUser,datetime.date.today().month,datetime.date.today().year)
    cal,leaveDays,presentDays,monthName,year = getCalendar(currentUser,datetime.date.today().month,datetime.date.today().year)
    leaves = find_leaves(currentUser)
    print(leaves)
    return render(request,"record.html",locals())

@login_required(login_url='/login')
def request(request):
    if request.method=="POST":
        type = request.POST.get("type")
        s_date = request.POST.get("s_date")
        e_date = request.POST.get("e_date")
        reason = request.POST.get("reason")        
        check_record1 = Leave.objects.all().filter(Employee_name=request.user,Start_date__range=[s_date,e_date],Pending_Status="Approved")
        check_record2 = Leave.objects.all().filter(Employee_name=request.user,End_date__range=[s_date,e_date],Pending_Status="Approved")
        print(check_record1,check_record2)
        if check_record1.__len__()==0 and check_record2.__len__()==0:
            Leave.objects.create(Employee_name = request.user,Start_date = s_date,End_date=e_date,Type = type,Reason=reason)
            return redirect("/history/")
        else:
            return redirect("/request/")
    return render(request, "request.html")   

def loginUser(request):
    if request.method=="POST":
        username = request.POST.get("username")
        print(username)
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(user)
            if datetime.date.today().strftime("%a") in ['Sat','Sun']:
                return redirect('/dashboard/')
            recordExist = Record.objects.all().filter(Employee_name=user,Date=datetime.datetime.today()).first()              
            print(recordExist)
            if recordExist==None:
                Record.objects.create(Employee_name=user)
            else:
                recordExist.Modified_time = recordExist.Logout_time
                recordExist.save() 

            print(recordExist)
            return redirect('/dashboard/')
    return render(request,"login.html")  

@login_required(login_url='/login')
def logoutUser(request):
    try:
        if datetime.date.today().strftime("%a") in ['Sat','Sun']:
            return redirect('/login/')
        recordExist = Record.objects.all().filter(Employee_name=request.user,Date=datetime.datetime.today()).first()              
        print(recordExist)
        if recordExist:
            recordExist.Logout_time = datetime.datetime.now()
            recordExist.save() 
        logout(request)
    except:
        pass
    return redirect('/login/')     


