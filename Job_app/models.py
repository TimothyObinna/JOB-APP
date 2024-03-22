# from django.db import models
# from django.contrib.auth.models import User
# from django.utils.text import slugify

# # Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
from .paystack import Paystack







class UserProfile(models.Model):
    UserInterest = (
    ('Tech', 'Tech'),
    ('Business', 'Business'),
    ('Company', 'Company'),
    ('Education', 'Education'),
    ('Bank', 'Bank'),
    ('Remote', 'remote')
)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length= 300, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=50, null=True, default=1)
    profile_image = models.ImageField(upload_to='profile')
    activation_key = models.CharField(max_length=300, blank=True, null=True)
    is_profile_updated = models.BooleanField(default=False)
    job_area_of_interest = models.CharField(choices=UserInterest, max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.user)


Application_Status = (
    ('Pending', 'Pending'),
    ('Delete', 'Delete'),
    ('Aproved', 'Aproved')
)



class Job(models.Model):
    Interest = (
    ('Select Here', 'Select Here'),
    ('Tech', 'Tech'),
    ('Business', 'Business'),
    ('Company', 'Company'),
    ('Education', 'Education'),
    ('Bank', 'Bank'),
    ('Remote', 'remote')
)
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    company = models.CharField(max_length=255)
    area_of_interest = models.CharField(choices=Interest, max_length=255)
    posted_date = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-posted_date']


class SavedJob(models.Model):
    Interest = (
    ('Select Here', 'Select Here'),
    ('Tech', 'Tech'),
    ('Business', 'Business'),
    ('Company', 'Company'),
    ('Education', 'Education'),
    ('Bank', 'Bank'),
    ('Remote', 'remote')
)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    # title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    company = models.CharField(max_length=255)
    area_of_interest = models.CharField(choices=Interest, max_length=255)
    saved_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
          return self.description
          
        # return f"{self.user.username}'s saved job"
    
class Meta:
    ordering = ['-saved_date']

Apply_choice = (
    ('apply_now', 'apply_now'),
    ('apply_later', 'apply_later')
)

class Application(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=300)
    address = models.CharField(max_length=300)
    dob = models.DateField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.FileField(upload_to='cover_letter/')
    apply_now = models.BooleanField(choices=Apply_choice, default=False)
    apply_later = models.BooleanField(choices=Apply_choice, default=False)
    application_status = models.CharField(choices=Application_Status, max_length=300, default='Pending')
    date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.full_name
    
    class Meta:
        ordering = ['-date']


notify = (
    ('New_Application_Submitted', 'New_Application_Submitted'),
    ('Application_Approved', 'Application_Approved'),
    ('Application_Declined', 'Application_Declined')
)

class AdminNotification(models.Model):
    admin_email = models.EmailField()
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    notification_type = models.CharField(choices=notify, max_length=50, default='New_Application_Submitted')  # 'Application Submitted', 'Application Approved', etc.
    

    def __str__(self):
        return self.admin_email


class EmployeeNotification(models.Model):
    employee_email = models.EmailField()
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    notification_type = models.CharField(choices=notify, max_length=50, default='Application_Approved')  # 'Application Approved', 'Application Rejected', etc.
    

    def __str__(self):
        return self.employee_email


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    notification_type = models.CharField(choices=notify, max_length=50, default='Application_Approved')  # 'New Job Posted', etc.
    

    def __str__(self):
        return self.notification_type



class AdminDashboardNotification(models.Model):
    admin_email = models.EmailField()
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    notification_type = models.CharField(choices=notify, max_length=50)  # 'New Application Submitted', etc.

    def __str__(self):
        return self.admin_email
    


class Payment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	amount = models.PositiveIntegerField(default=500)
	ref = models.CharField(max_length=200)
	email = models.EmailField()
	verified = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True)
	job = models.ForeignKey(Job, on_delete=models.CASCADE, default=2)

	class Meta:
		ordering = ('-date_created',)

	def __str__(self):
		return f"Payment: {self.amount}"

	def save(self, *args, **kwargs):
		while not self.ref:
			ref = secrets.token_urlsafe(50)
			object_with_similar_ref = Payment.objects.filter(ref=ref)
			if not object_with_similar_ref:
				self.ref = ref

		super().save(*args, **kwargs)
	
	def amount_value(self):
		return int(self.amount) * 100

	def verify_payment(self):
		paystack = Paystack()
		status, result = paystack.verify_payment(self.ref, self.amount)
		if status:
			if result['amount'] / 100 == self.amount:
				self.verified = True
			self.save()
		if self.verified:
			return True
		return False
    



    


	




# class Userprofile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     email = models.EmailField(max_length=300, blank=True, null=True)
#     address = models.CharField(max_length= 300, blank=True, null=True)
#     dob = models.DateField(blank=True, null=True)
#     fullname = models.CharField(max_length=100, blank=True, null=True)
#     username = models.CharField(max_length=50, null=True, default=1)
#     profile_image = models.ImageField(upload_to='profile')
#     activation_key = models.CharField(max_length=300, blank=True, null=True)

#     def __str__(self):
#         return str(self.user)



        


# class Company(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     # industry = models.CharField(max_length=100)

#     def __str__(self):
#         return self.name
    


# class Job(models.Model):
#     posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     requirements = models.TextField()
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
#     posted_on = models.DateTimeField(auto_now_add=True)
   


#     def __str__(self):
#         return self.title
    
#     class Meta:
#         ordering = ['-posted_on']

    



# Status = (
#     ('Pending', 'Pending'),
#     ('Approved', 'Approved')
# )



# class JobCreationLog(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Job created by {self.user.username} at {self.created_at}"


# class Application(models.Model):
#     applicant = models.ForeignKey(User, on_delete=models.CASCADE)
#     job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
#     resume = models.FileField(upload_to='resumes/')
#     cover_letter = models.FileField(upload_to='cover_letter/')
#     applied_at = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(choices=Status, default='Pending', max_length=300)

#     def __str__(self):
#         return f"{self.applicant.username} - {self.job.title}"
    
#     class Meta:
#         ordering = ['-applied_at']

# Status = (
#     ('Apply_later', 'Apply_later')
# )

    


# class Interview(models.Model):
#     application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='interview')
#     interview_date = models.DateTimeField()
#     location = models.CharField(max_length=255)
#     notes = models.TextField()

#     def __str__(self):
#         return f"{self.application.applicant.username} - {self.application.job.title} Interview"
    


# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_read = models.BooleanField(default=False)

#     def __str__(self):
#         return self.message



# class Author(models.Model):
#     profile = models.ImageField(upload_to='Profile')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     display_name = models.CharField(max_length=200)
#     full_name = models.CharField(max_length=255, blank=True, null=True)
#     profession = models.CharField(max_length=255, blank=True, null=True)
#     about_me = models.TextField(blank=True, null=True)
#     twitter_handle = models.CharField(max_length=255, blank=True, null=True)
#     facebook_handle = models.CharField(max_length=255, blank=True, null=True)
#     telegram_channel = models.CharField(max_length=255, blank=True, null=True)
#     instagram_handle = models.CharField(max_length=255, blank=True, null=True)


#     def __str__(self):
#         return self.display_name

# Status = (
#     ('Pending', 'Pending'),
#     ('Delete', 'Delete'),
#     ('Aproved', 'Aproved')
# )


# class Post(models.Model):
#     title = models.CharField(max_length=200)
#     body = models.TextField(max_length=10000)
#     upload_image = models.ImageField(upload_to='blog')
#     date_created = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(choices=Status, default='Pending', max_length=300)
#     author = models.ForeignKey(User, on_delete=models.CASCADE)
#     # category = models.CharField(max_length=200)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE, default=10)

#     def __str__(self):
#         return self.title
    
#     class Meta:
#         ordering = ['-date_created']