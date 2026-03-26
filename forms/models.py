from django.db import models


class FormResponse(models.Model):
    lead_email = models.EmailField(unique=True)
    current_step = models.IntegerField(default=0)

    taskid = models.CharField(max_length=255, null=True, blank=True)

# step 1
    interested = models.BooleanField(null=True, blank=True)
    reschedule = models.BooleanField(null=True, blank=True)
    preferred_date = models.DateField(null=True, blank=True)

# step 2
    proposed_time_ok = models.BooleanField(null=True, blank=True)
    preferred_time = models.CharField(max_length=20, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

# step 3
    final_confirmation = models.CharField(max_length=20, null=True, blank=True)
    communication_channel = models.CharField(max_length=20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)