from django.core.management.base import BaseCommand, CommandError
from movieindex import models
from django.core import serializers
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        categories = serializers.serialize("json", models.MovieCategory.objects.all())
        folders = serializers.serialize("json", models.MovieFolder.objects.all())
        movies = serializers.serialize("json", models.Movie.objects.all(), 
            fields = ('folder','category', 'subpath', 'added', 'active', 'title', 'rating', 'tags'))
        tags = serializers.serialize("json", models.Tag.objects.all())
        r = {
            "categories": categories,
            "folders": folders,
            "movies": movies,
            "tags": tags
        }
        print(json.dumps(r))