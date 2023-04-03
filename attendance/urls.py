from django.contrib import admin
from django.urls import path
from management import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.loginUser,name="login"),
    path('approval/<int:leaveId>/<int:status>/',views.decision,name="decision"),
    path('approval/',views.approval,name="approval"),
    path('',views.home,name="home"),
    path('record/<int:Employee_id>/',views.seekEmployeeRecord,name = "chooseRecord"),
    path('record/<int:Employee_id>/<int:year>/<int:month>',views.seekEmployeeRecord,name = "chooseRecord"),
    path('record/',views.record,name="record"),
    path('request/',views.request,name="request"),
    path('history/',views.history,name="history"),
    path('logout/',views.logoutUser,name="logout"),
    path('dashboard/',views.dashboard),
]

admin.site.site_header = "Attendance and Leave Management System"
admin.site.site_title = "Admin Area"
admin.site.index_title = "Welcome To The Admin Area..."