from __future__ import unicode_literals

from django.db import models

# Create your models here.
class MovieFolder(models.Model):
    name = models.CharField(max_length=100)
    folder = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name
    
class Movie(models.Model):
    folder = models.ForeignKey(MovieFolder)
    subpath = models.CharField(max_length=200)
    