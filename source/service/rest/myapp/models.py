from django.db import models

class mysite(models.Model):
    title = models.CharField(max_length=100)
    num = models.IntegerField()

    class Meta:
        ordering = ['num']

class mypost(models.Model):
    title = models.CharField(max_length=100)