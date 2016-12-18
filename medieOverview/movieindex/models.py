from __future__ import unicode_literals

from django.db import models, transaction
from django.conf import settings

from film_parser import MovieDataExtractor
from video_extracter import MovieDataExtractorFFmpeg

import os.path
from get_username import get_username
from django.urls import reverse

from django.contrib.auth.models import User
from django.urls import reverse

fetcher = MovieDataExtractorFFmpeg(settings.FFMPEG)
extractor = MovieDataExtractor(fetcher)

# Create your models here.
class MovieFolder(models.Model):
    name = models.CharField(max_length=100)
    folder = models.CharField(max_length=200)
    default_category = models.ForeignKey("MovieCategory")
    last_scanned = models.DateTimeField(blank=True, null=True)
    
    def file_exists(self, subpath):
        return self.movie_set.filter(subpath=subpath).exists()
    
    def __unicode__(self):
        return self.name

    def get_movie(self, fullpath):
        if fullpath.startswith(self.folder):
            fp = fullpath[len(self.folder):].lstrip("\\")
            return self.movie_set.filter(subpath = fp).first()
    
    def add_movie(self, subpath, category, tags=[]):
        with transaction.atomic():
            path = os.path.join(self.folder, subpath)
            data = extractor.get_movie_data(path)
            m = Movie(**data["movie"])
            m.folder = self
            m.subpath = subpath
            m.category = category
            m.save()
            
            for e in data["screens"]:
                m.add_thumb( e["data"], e["seconds"])        
            
            for tag in tags:
                m.add_tag(tag)

    class Meta:
        permissions = (
            ("scan_folder", "Can scan folder"),
        )
        
class MovieCategory(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name
    
    def user_access(self, user):
        return True
    
class Movie(models.Model):
    folder = models.ForeignKey(MovieFolder)
    category = models.ForeignKey(MovieCategory)
    subpath = models.CharField(max_length=200, db_index=True)
    added = models.DateTimeField(auto_now=True)
    
    rating = models.IntegerField(default = 0)
    metadata = models.TextField(blank = True)
    
    title = models.CharField(max_length=200)
    length = models.IntegerField(default = 0)
    size = models.IntegerField()
    bitrate = models.IntegerField()
    codec = models.CharField(max_length=20)
    fps = models.FloatField()
    height = models.IntegerField()
    width = models.IntegerField()
    
    main_thumb = models.ForeignKey('Thumb', null=True, blank = True, related_name="movie2")
    tags = models.ManyToManyField("Tag", related_name="movies", blank=True)
    
    def get_path(self):
        return os.path.join(self.folder.folder, self.subpath)
    
    def play_file(self):
        os.startfile(self.get_path())
    
    def get_tags(self):
        return self.tags.all()

    def user_access(self, user):
        return self.category.user_access(user)

    def get_download_url(self):
        return reverse("movie-download", args=(self.id,))
    
    def get_tag_url(self):
        return reverse("movie-addtag", args=(self.id,))
    
    def get_json_url(self):
        return reverse("movie-json-detail", args=(self.id,))
    
    def add_tag(self, tag):
        if tag:
            tag, created = Tag.objects.get_or_create(name = tag)
            tag.movies.add(self)
            self.log("Added tag %s" % tag)
            tag.update_count()
    
    def get_thumbs(self):
        return self.thumbs.all()
    
    def log(self, entry):
        user = get_username().user
        return MovieLog.objects.create(user=user, movie=self, entry=entry)
    
    class Meta:
        permissions = (
            ("download_movie", "Can download movie"),
            ("play_movie", "Can play movie"),
            ("tag_movie", "Can tag movie"),
        )
    
    def add_thumb(self, data, timestamp):
        t = Thumb()
        t.timestamp = timestamp
        t.movie = self
        t.image = data
        t.save()
        
        if not self.main_thumb:
            self.main_thumb = t
            self.save()
    
    def __unicode__(self):
        return self.title

class MovieLog(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    movie = models.ForeignKey(Movie)
    entry = models.TextField()
    added = models.DateTimeField(auto_now=True)
    
class Tag(models.Model):
    name = models.CharField(unique = True, max_length=20)
    count = models.IntegerField(default = 0)
    
    def __unicode__(self):
        return self.name

    def update_count(self):
        self.count = self.movies.count()
        self.save()
        
    class Meta:
        ordering = ["name"]

class Thumb(models.Model):
    movie = models.ForeignKey(Movie, related_name='thumbs')
    timestamp = models.IntegerField(default = 0)
    image = models.BinaryField()
    
    def get_image_url(self):
        return reverse("thumb-show", args=(self.id,))
    
    def __unicode__(self):
        return u"Thumb for %s [%s]" % ( self.movie, self.timestamp)