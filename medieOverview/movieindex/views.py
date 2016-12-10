from . import models
from django.views.generic import ListView
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, StreamingHttpResponse
# Create your views here.
from . import scanner
import os

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required

from mimetypes import MimeTypes

from ranged_fileresponse import RangedFileResponse

@login_required
def display_image(request, imageid):
    thumb = models.Thumb.objects.get(id=imageid)
    r = HttpResponse(thumb.image, content_type="image/jpeg")
    r["Cache-Control"] = "max-age=31536000"
    return r

class MFolderIndex(ListView, LoginRequiredMixin):
    model = models.MovieFolder

class MoviesIndex(ListView, LoginRequiredMixin):
    model = models.Movie
    paginate_by = 100
    context_object_name = 'movies'
    
    def get_queryset(self):
        Q = models.Movie.objects.all()
        for tag in self.request.GET.getlist("tag"):
            Q = Q.filter(tags__name = tag)
        return Q
    
    def get_context_data(self, **kwargs):
        context = super(MoviesIndex, self).get_context_data(**kwargs)
        context['tags'] = models.Tag.objects.all()
        return context

@permission_required("movieindex.download_movie")    
def download_movie(request, movieid):
    movie = models.Movie.objects.get(id=movieid)
    filename = movie.get_path()
    mime = MimeTypes().guess_type(filename)[0]
    fr = RangedFileResponse(request, filename, content_type=mime)
    fr['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(filename)
    return fr

@permission_required("movieindex.play_movie")    
def play_movie(request, movieid):
    movie = models.Movie.objects.get(id=movieid)
    movie.play_file()
    return HttpResponse("OK")

@permission_required("movieindex.scan_folder")
def scan_moviefolder(request, mfid):
    mf = models.MovieFolder.objects.get(id=mfid)
    c = models.MovieCategory.objects.get(id=1)
    
    def iter_response():
        yield u"<div>Scanning folder '%s'...</div><br/>" % mf.name
        yield u"<table>"
        for root, f, status in scanner.scan(mf, c):
            if status != "Skipped" or request.GET.get("showskip"):
                root = root[:-len(f)]
                yield u"<tr><td>%s</td> <td>%s</td> <td>%s</td></div>" % (root, f, status)
        yield u"</table>Scan done"
        
    return StreamingHttpResponse(iter_response())