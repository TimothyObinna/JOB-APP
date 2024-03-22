
from .models import JobCreationLog

def count_new_jobs():
    new_jobs_count = JobCreationLog.objects.count()
    return new_jobs_count