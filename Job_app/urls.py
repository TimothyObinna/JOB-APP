from django.urls import path
from .views import *



urlpatterns = [
    path('Login', Login.as_view(), name='login'),
    path('logout/', Logout, name='logout'),
    path("", Myview.as_view(), name="dashboard"),
    path("signup", Signup.as_view(), name="signup"),
    path('register/<int:pk>/', Register.as_view(), name='register'),
    path('register/<str:activation_key>/', RegisterActivationView.as_view(), name='register_activation'),
    # path('forgot-password/', ForgotPassword.as_view(), name='forgot-password'),
    # path('reset/<str:uidb64>/<str:token>/', PasswordResetConfirm.as_view(), name='password_reset_confirm'),

    path("Job_Details/<int:pk>", Job_details.as_view(), name='jobdetails'),
    path('apply/<int:pk>/', ApplyJobView.as_view(), name='apply_job'),

    path('Applications/', Apply_list.as_view(), name='app-list'),
    path('Applications/', User_Apply_list.as_view(), name='userapp-list'),
    path('Approved/', Approved_list.as_view(), name='approved'),
   

    
    # path("Notification", create_job_notification, name='notify'),
    # path("Dashboard", create_job_notification, name='dboard'),
    # path('new-jobs-count/', display_new_jobs_count, name='new_jobs_count'),

    path('', BaseProfileView.as_view(), name='userprofile'),
    path('profilepage/', ProfilePage.as_view(), name='profilepage'),
    path('profileupdate', UserProfileUpdateView.as_view(), name='updateprofile'),

    path('create_job/', CreateJobView.as_view(), name='create_job'),
    path('Edit_Job_Advert/<int:pk>/', Edit_Job.as_view(), name='edit_job'),
    path('Delete_Advert/<int:pk>', Delete_Job.as_view(), name='job_delete'),
    path('approve_application/<int:pk>/', ApproveApplicationView.as_view(), name='approve_application'),
    path('Disapprove/<int:pk>/', Dis_ApproveApplicationView.as_view(), name='disapproved'),
    path('Delete_Application/<int:pk>', Delete_Application.as_view(), name='delete_app'),

    # path('ApplicationCheck/', ApplicationCheck.as_view(), name='check_app'),
    path('initiate-payment/', initiate_payment, name='initiate_payment'),
	path('verify-payment/<str:ref>/', verify_payment, name='verify_payment'),

    path('save-job/<int:pk>/', SaveJob.as_view(), name='save_job'),
    path('Saved_job/<str:ref>/', SavedAdvert.as_view(), name='saved-add'),

]