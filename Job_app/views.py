from django.shortcuts import render, redirect, HttpResponse
from django.views.generic import View, ListView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from .models import *
import uuid
from django.contrib import messages
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Payment
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Sum
from datetime import datetime

# Create your views here.
from django.db.models.signals import post_save
from django.dispatch import receiver


# Dashboard

class Myview(View):
    def get(self, request):
        jobs = Job.objects.all()
        admin = AdminNotification.objects.all().acount()

        context = {
            'jobs': jobs,
            'admin':admin
        }
        return render(request, 'index.html', context=context)
       
    
    def post(self, request):
        return render(request, 'index.html')
    

# This is signup view

class Signup(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'signup.html')
    
    def post(self, request):
        if request.method == 'POST':
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            password2 = request.POST.get('password2')

            if password != password2:
              return render(request, 'signup.html', {'error': 'Passwords do not match'})

            # Create a user without saving it to the database
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
            # Generate a link for completing the registration
            activation_key = str(uuid.uuid4())
            profile = UserProfile.objects.create(user=user, activation_key=activation_key)
            registration_link = f"http://127.0.0.1:8000/register/{profile.activation_key}/"

            # Send registration link to the user's email
            send_mail(
                'Complete Your Registration',
                f'Use this link to complete your registration: {registration_link}',
                'ewatimothyobinna@gmail.com',
                [email],
                fail_silently=False,
            )
            return HttpResponse('Check your mail for link to complete your registration')
        



# This is the registration activation view

class RegisterActivationView(View):
    def get(self, request, activation_key):
        try:
            # Find the user profile with the given activation key
            profile = UserProfile.objects.get(activation_key=activation_key)
            # Activate the associated user
            user = profile.user
            user.is_active = True
            user.save()
            # Render a success page or redirect to registration page
            messages.success(request, 'Activation successful. You can now continue with your registration.')
            # return redirect('register')
            return render(request, 'register.html', {'user':user})

        except UserProfile.DoesNotExist:
            # Render an error page or redirect to an error page
            messages.error(request, 'Invalid activation key. Please contact support.')
            return redirect('error_page')
        


# This is the registration view
class Register(View):
    def get(self, request, *args, **kwargs):

        jobpost = Job.Interest

        context= {
            'Interest':jobpost
        }

        return render(request, 'register.html', context=context)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            # Retrieve data from the form
            fullname = request.POST.get('fullname')
            address = request.POST.get('address')
            dob = request.POST.get('dob')
            area_of_interest = request.POST.get('area_of_interest')

            # Retrieve the existing user based on the provided primary key (pk)
            user_pk = kwargs.get('pk')
            user = User.objects.get(pk=user_pk)

            # Create or update the user profile
            profile, profile_created = UserProfile.objects.get_or_create(user=user)
            profile.fullname = fullname
            profile.address = address
            profile.dob = dob
            profile.job_area_of_interest = area_of_interest
            profile.save()
            return redirect('login')  # Redirect to a login page
        return render(request, 'register.html')


# This is the Login view
class Login(View):
    def get(self, request):
        return render(request, 'login.html') 
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Username and password are required!")
            return redirect('login')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User not found!")
            return redirect('login')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Login succesful. {request.user}, Welcome to home page.")
            return redirect('dashboard')
            # Check if the user has an updated profile
            # if UserProfile.objects.filter(user=user).exists():
            #     return redirect('dashboard')
            # else:
            #     return redirect('updateprofile')  # Redirect to the profile update page
        else:
            messages.error(request, "Incorrect password, try again!")
            return redirect('login')



# This is the logout function
def Logout(request):
    logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('dashboard')



# This is the base profile view
class BaseProfileView(View):
    
    def get_profile_info(self, user):
        try:
            profile = get_object_or_404(UserProfile, user=user)  # Access the related Profile using the lowercased name
        
            profile_info = {
                'profile_image_url': profile.profile_image if profile.profile_image else None,
                'username': profile.fullname,
                'fullname': profile.fullname,
                'email': profile.user.email,
                'address': profile.address,
                'dob': profile.dob,
                'user': profile.user,
            }

            return {'profile_info': profile_info}

        except UserProfile.DoesNotExist:
            return {}



# This is the profile page view
class ProfilePage(LoginRequiredMixin, BaseProfileView):
    login_url = 'login'
    def get(self, request):
        context = self.get_profile_info(request.user)
        if not context:
            return redirect('dashboard')
        return render(request, 'profile.html', context=context)
    
    def post(self, request):
        # Process the submitted form data
        return render(request, 'profile.html')
    
    
# This is the profile update view
class UserProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'profile_update.html'

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(UserProfile, user=request.user)
        context = {'profile': profile}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(UserProfile, user=request.user)

        # Update profile fields based on POST data
        profile.fullname = request.POST.get('fullname')
        profile.address = request.POST.get('address')
        profile.dob = request.POST.get('dob')

        # Handle profile image
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            profile.profile_image = profile_image

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profilepage')



# This is the begining of create job view
class CreateJobView(LoginRequiredMixin, View):
    login_url = 'login'

    template_name = 'create_job.html'

    def get(self, request):

        jobpost = Job.Interest

        context= {
            'Interest':jobpost
        }
        return render(request, self.template_name, context=context)
    

    def post(self, request):
        posted_by = request.user
        title = request.POST.get('title')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        company = request.POST.get('company')
        area_of_interest = request.POST.get('area_of_interest')
        

        job = Job.objects.create(
            title=title,
            description=description,
            requirements=requirements,
            company=company,
            area_of_interest=area_of_interest,
            posted_by= posted_by
            
        )
        messages.success(request, "Job Advert created successfully")

        # Redirect to the job listing page or any other desired URL
        return redirect('dashboard')
    

# This is the begining of edit job view
class Edit_Job(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        job_post = get_object_or_404(Job, pk=pk)
        jobpost = Job.Interest

        context = {
            'job_post':job_post,
            'Interest':jobpost
        }
        return render(request, 'edit_advert.html', context=context)
    


    def post(self, request, pk):
        job_post = Job.objects.get(pk=pk)

        posted_by = request.user
        title = request.POST.get('title')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        company = request.POST.get('company')
        area_of_interest = request.POST.get('area_of_interest')

        # Update the existing post instance with the new data
        job_post.posted_by = posted_by
        job_post.title = title
        job_post.description = description
        job_post.requirements = requirements
        job_post.company = company
        job_post.area_of_interest = area_of_interest

        job_post.save()
        messages.success(request, "Job Advert edited successfully")
        return redirect('dashboard')


# This is the begining of delete job view
class Delete_Job(LoginRequiredMixin, View):
    login_url = 'login'
    def get(self, request, pk):
        try:
            posts = get_list_or_404(Job, pk=pk)
        except Job.DoesNotExist:
            return HttpResponse('Job Not Found')
            
        context={
            'jobdel': posts,
        }
        return render(request, 'delete_job.html', context=context)
    

    def post(self, request, pk):
        posts = get_object_or_404(Job, pk=pk)
        posts.delete()
        messages.error(request, "Job Advert deleted successfully")
        return redirect('dashboard')
    


# This is the begining of job details view
class Job_details(LoginRequiredMixin, ListView):
    login_url = 'login'

    def get(self, request,pk):
        # post_details = Post.objects.get(pk=pk)
        job_details = get_object_or_404(Job,pk=pk)


        context = {
            'job_details': job_details
        }
        return render(request,'details.html',context=context)
    

    def post(self, request,pk):
        # post_details = Post.objects.get(pk=pk)
        job_details = get_object_or_404(Job,pk=pk)
        context = {
            'job_details':job_details
        }

        return render(request,'details.html',context=context)
    



# This is the begining of job application view
class ApplyJobView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        job = Job.objects.get(pk=pk)
        applicant = request.user

        # Check if the user has already applied for this job
        existing_application = Application.objects.filter(job=job, applicant=applicant).exists()
        if existing_application:
            # Handle the case where the user has already applied
            messages.error(request, "You have already applied for this job. Double application is not allowed.")
            return redirect("dashboard")
        

        return render(request, 'apply.html', {'job': job})

    def post(self, request, pk):
        job = Job.objects.get(pk=pk)
        applicant = request.user
        

        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        dob = request.POST.get('dob')
        resume = request.FILES.get('resume')
        cover_letter = request.FILES.get('cover_letter')

        # Create application object
        application = Application.objects.create(
            job=job,
            applicant=applicant,
            full_name=full_name,
            address=address,
            dob=dob,
            resume=resume,
            cover_letter=cover_letter,
        )

        # Generate PDF with application information
        pdf_file_path = f'media/applications/application_{application.id}.pdf'
        self.generate_pdf(full_name, address, dob, pdf_file_path)

        # Send email notification to admin with PDF attachment
        admin_email = 'etoontop@gmail.com'  # Replace with actual admin email
        subject = 'New Job Application Submitted'
        message = 'Please find attached the application details.'
        email = EmailMessage(
            subject,
            message,
            'ewatimothyobinna@gmail.com',
            [admin_email],
        )
        email.attach_file(pdf_file_path)
        email.send()

        # Create AdminNotification object
        AdminNotification.objects.create(
            admin_email=admin_email,
            job=job,
            applicant=applicant,
            notification_type='New_Application_Submitted'
        )
        messages.success(request, f'Aplication for {job} submitted successfully')

        return redirect('dashboard')

    def generate_pdf(self, full_name, address, dob, file_path):
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "Full Name: " + full_name)
        c.drawString(100, 730, "Address: " + address)
        c.drawString(100, 710, "Date of Birth: " + dob)
        c.save()



# This is the begining of application list view
class Apply_list(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        
        app_list = Application.objects.filter(application_status='Pending')

        context = {
            'app_list':app_list
        }
        return render(request, 'application_list.html', context=context)
    

# This is the begining of user application list view
class User_Apply_list(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):

        current_user = request.user
        
        app_list = Application.objects.filter(applicant=current_user, application_status='Pending')

        context = {
            'app_list':app_list
        }
        return render(request, 'application_list.html', context=context)
    

# This is the begining of approved application list view
class Approved_list(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        
        approved = Application.objects.filter(application_status='Approved')

        context = {
            'approved':approved
        }
        return render(request, 'Approved.html', context=context)
    

# This is the begining of approve application view
class ApproveApplicationView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk, *args, **kwargs):
        application = Application.objects.get(pk=pk)
        context = {'application': application}
        return render(request, 'approve_apply.html', context=context)

    def post(self, request, *args, **kwargs):
        application_id = kwargs.get('pk')
        application = Application.objects.get(pk=application_id)

        # Update the application status to 'Approved'
        application.application_status = 'Approved'
        application.save()

        # Create a UserNotification for the applicant
        UserNotification.objects.create(
            user=application.applicant,
            job=application.job,
            notification_type='Application_Approved')

        # Send email notification to the applicant
        subject = 'Application Approved'
        message = f'{application.full_name}, your application for the job "{application.job}" has been approved. A notification for the date of interview will be sent to you via Email. Check your email regularly for our notification. Congratulations!'
        send_mail(subject, message, 'ewatimothyobinna@gmail.com', [application.applicant.email])

        messages.success(request, f'You have successfully approved the application submitted by {application.full_name} for the job "{application.job}".')

        # Redirect to a relevant page after approval
        return redirect('approved')


# This is the begining of disapprove application view
class Dis_ApproveApplicationView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk,  *args, **kwargs):
        application = Application.objects.get(pk=pk)
        context = {'application':application}
        return render(request, 'Dis_approve_apply.html', context=context)

    def post(self, request, *args, **kwargs):
        application_id = kwargs.get('pk')
        # Retrieve the application object
        # application = Application.objects.get(pk=pk)
        application = Application.objects.get(pk=application_id)

        # Update the application status to 'Approved'
        application.application_status = 'Pending'
        application.save()

        # Redirect to a relevant page after approval
        return redirect('approved') 
    

# This is the begining of delete application view
class Delete_Application(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        try:
            app = get_list_or_404(Application, pk=pk)
        except Job.DoesNotExist:
            return HttpResponse('Application Not Found')
            
        context={
            'appdel': app,
        }
        return render(request, 'Delete_App.html', context=context)
    

    def post(self, request, pk):
        posts = get_object_or_404(Application, pk=pk)
        posts.delete()
        return redirect('userapp-list')
    

class ApplicationCheck(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk, *args, **kwargs):
        job = Job.objects.get(pk=pk)
        applicant = request.user

        context = {
            'job': job
        }

        # Check if the user has already applied for this job
        existing_application = Application.objects.filter(job=job, applicant=applicant).exists()
        if existing_application:
            # Handle the case where the user has already applied
            return HttpResponse("You have already applied for this job.")
        else:
            # Redirect to the initiate_payment view if the user does not have an existing application
            return redirect('initiate_payment', context=context)


# This is the begining of payment view

def initiate_payment(request):
    
	if request.method == "POST":
		amount = 500
		email = request.POST['email']

        

		pk = settings.PAYSTACK_PUBLIC_KEY

		payment = Payment.objects.create(amount=amount, email=email, user=request.user)
		payment.save()

		context = {
			'payment': payment,
			'field_values': request.POST,
			'paystack_pub_key': pk,
			'amount_value': payment.amount_value(),
		}
		return render(request, 'make_payment.html', context)

	return render(request, 'payment.html')


def verify_payment(request, ref):
    payment = get_object_or_404(Payment, ref=ref)
    verified = payment.verify_payment()

    if verified:
        print(request.user.username, " payment successfully")
         # Assuming Job is your model and you want to redirect to the ApplyJobView with the pk of the job
        pk = payment.job.pk  # Adjust this line based on your model structure
        return redirect('apply_job', pk=pk)
    else:
        return render(request, "payment.html")



from django.shortcuts import render
from .models import UserNotification

def notification_count(request):
    # Count objects in UserNotification
    notification_count = UserNotification.objects.count()

    # Render template with count value
    return render(request, 'header.html', {'notification_count': notification_count})




class SaveJob(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        context = {
            'jobsave': job
        }
        return render(request, 'save_job.html', context=context)


    def post(self, request, pk, *args, **kwargs):
         # Get the job object
        job = get_object_or_404(Job, pk=pk)

        # Check if the job is already saved by the user
        if SavedJob.objects.filter(user=request.user, job=job).exists():
            messages.warning(request, 'Sorry, this job is already saved. You cannot save a job twice.')
            return redirect('jobdetails', pk=pk)

        # Save the job for the user
        saved_job = SavedJob.objects.create(
            user=request.user, 
            job=job, 
            description=job.description,
            requirements=job.requirements,
            company=job.company,
            area_of_interest=job.area_of_interest,

            )
        messages.success(request, 'Job saved successfully.')
        return redirect('jobdetails', pk=pk)


class SavedAdvert(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request, pk):
        # Retrieve saved jobs for the logged-in user

        saved_jobs = SavedJob.objects.filter(user=request.user, pk=pk)
        

        context = {
            'saved_jobs': saved_jobs,

        }

        # Pass the saved jobs to the template
        return render(request, 'saved-jobs.html', context=context)
    







