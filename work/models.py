from django.db import models


class WorkItem(models.Model):
    sleep_seconds = models.IntegerField()
    task_id = models.CharField(max_length=30, null=True)
    status = models.CharField(max_length=30, null=30)
