from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(UserProfile)
class UserProfile(admin.ModelAdmin):
    list_display = ('user', 'email', 'address', 'dob', 'fullname', 'username', 'profile_image', 'activation_key', 'is_profile_updated', 'job_area_of_interest')

@admin.register(Job)
class Job(admin.ModelAdmin):
    list_display = ('title', 'description', 'company', 'area_of_interest', 'posted_date', 'posted_by')

@admin.register(SavedJob)
class SavedJob(admin.ModelAdmin):
    list_display = ('user', 'job', 'description', 'requirements', 'company', 'area_of_interest', 'saved_date')

@admin.register(Application)
class Application(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'full_name', 'address', 'dob', 'resume', 'cover_letter', 'apply_now', 'apply_later', 'application_status', 'date')


@admin.register(AdminNotification)
class AdminNotification(admin.ModelAdmin):
    list_display = ('admin_email', 'applicant', 'job', 'notification_type')


@admin.register(EmployeeNotification)
class EmployeeNotification(admin.ModelAdmin):
    list_display = ('employee_email', 'applicant', 'job', 'notification_type')

@admin.register(UserNotification)
class UserNotification(admin.ModelAdmin):
    list_display = ('user', 'job', 'notification_type')

@admin.register(AdminDashboardNotification)
class AdminDashboardNotification(admin.ModelAdmin):
    list_display = ('admin_email', 'job', 'notification_type')



@admin.register(Payment)
class Payment(admin.ModelAdmin):
    list_display = ('user', 'amount', 'ref', 'email', 'verified', 'date_created')






# @admin.register(Userprofile)
# class Userprofiler(admin.ModelAdmin):
#     list_display = ('user', 'email', 'fullname', 'username', 'address')


# @admin.register(Company)
# class Company(admin.ModelAdmin):
#     list_display = ('name', 'description')



# @admin.register(Job)
# class Job(admin.ModelAdmin):
#     list_display = ('posted_by', 'title', 'description', 'company', 'posted_on')


# @admin.register(Application)
# class Application(admin.ModelAdmin):
#     list_display = ('applicant', 'resume', 'cover_letter', 'applied_at', 'status')


# @admin.register(Interview)
# class Interview(admin.ModelAdmin):
#     list_display = ('application', 'interview_date', 'location', 'notes')



