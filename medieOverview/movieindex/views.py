from django.shortcuts import render
from . import models
from django.views.generic import TemplateView, ListView
from django.http import HttpResponse
# Create your views here.

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@login_required
def display_image(request, imageid):
    thumb = models.Thumb.objects.get(id=imageid)
    r = HttpResponse(thumb.image, content_type="image/jpeg")
    r["Cache-Control"] = "max-age: 31536000"
    return r

class MoviesIndex(ListView):
    model = models.Movie
    
    def get_context_data(self, **kwargs):
        context = super(MoviesIndex, self).get_context_data(**kwargs)
        context['tags'] = models.Tag.objects.all()
        return context
    
def play_movie(request, movieid):
    movie = models.Movie.objects.get(id=movieid)
    movie.play_file()
    return HttpResponse("OK")