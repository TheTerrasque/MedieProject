from . import models
from django.views.generic import ListView
from django.views.generic.detail import BaseDetailView
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
# Create your views here.
from . import scanner
import os
from django.core.serializers import json, serialize

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth.decorators import login_required

from mimetypes import MimeTypes

from ranged_fileresponse import RangedFileResponse
import datetime

from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from mixins import JSONResponseMixin

@login_required
def display_image(request, imageid):
    thumb = models.Thumb.objects.get(id=imageid)
    r = HttpResponse(thumb.image, content_type="image/jpeg")
    r["Cache-Control"] = "max-age=31536000"
    return r

@csrf_exempt
@permission_required("movieindex.tag_movie")
def tagMovie(request, pk):
    movie = models.Movie.objects.get(id=pk)
    if not movie.user_access(request.user): return HttpResponse("BAD")
    tag = request.POST.get("tag")
    movie.add_tag(tag)
    return HttpResponse("OK")


@login_required
def jsonMovie(request, pk):
    movie = models.Movie.objects.get(id=pk)
    if not movie.user_access(request.user): return "BAD"
    d = {
        "id": movie.id,
        "title": unicode(movie),
        "thumbs": [x.get_image_url() for x in movie.get_thumbs()],
        "tags": [{"name":x.name} for x in movie.tags.all()],
        "path": unicode(movie.folder),
        "tagurl": movie.get_tag_url(),
        "url": movie.get_json_url(),
    }
    return JsonResponse(d)
    
class MFolderIndex(LoginRequiredMixin, ListView):
    model = models.MovieFolder

class MoviesIndex(LoginRequiredMixin, ListView):
    model = models.Movie
    paginate_by = 100
    context_object_name = 'movies'
    
    def get_queryset(self):

        mcs = [
            x for x in models.MovieCategory.objects.all()
            if x.user_access(self.request.user)
            ]
        Q = models.Movie.objects.filter(category__in=mcs)
        
        for tag in self.get_tags():
            Q = Q.filter(tags__id = tag)
        return Q
    
    def get_tags(self):
        t = self.kwargs.get("tags", [])
        if t:
            t=t.split(",")
        r = [int(tn) for tn in t]
        return r
    
    def get_context_data(self, **kwargs):
        context = super(MoviesIndex, self).get_context_data(**kwargs)
        ct = models.Tag.objects.filter(id__in=self.get_tags())
        context['ctags'] = ct
        context['sctags'] = ",".join([str(x.id) for x in ct] + [""])
        context['tags'] = models.Tag.objects.filter(movies__in=self.get_queryset()).distinct()
        return context

@permission_required("movieindex.download_movie")    
def download_movie(request, movieid):
    movie = models.Movie.objects.get(id=movieid)
    if not movie.user_access(request.user): return "BAD"
    filename = movie.get_path()
    movie.log("Downloaded movie")
    mime = MimeTypes().guess_type(filename)[0]
    fr = RangedFileResponse(request, filename, content_type=mime)
    fr['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(filename)
    return fr

@permission_required("movieindex.play_movie")    
def play_movie(request, movieid):
    movie = models.Movie.objects.get(id=movieid)
    if not movie.user_access(request.user): return "BAD"
    movie.play_file()
    movie.log("Played movie")
    return HttpResponse("OK")

@permission_required("movieindex.scan_folder")
def scan_moviefolder(request, mfid):
    mf = models.MovieFolder.objects.get(id=mfid)
    c = mf.default_category
    mf.last_scanned = datetime.datetime.now()
    mf.save()
    
    def iter_response():
        yield u"<div>Scanning folder '%s'...</div><br/>" % mf.name
        yield u"<table>"
        for root, f, status in scanner.scan(mf, c):
            if status != "Skipped" or request.GET.get("showskip"):
                root = root[:-len(f)]
                yield u"<tr><td>%s</td> <td>%s</td> <td>%s</td></div>" % (root, f, status)
        yield u"</table>Scan done"
        
    return StreamingHttpResponse(iter_response())

@permission_required("movieindex.tag_movie")
def json_tags(request):
    startswith = request.GET.get("text")
    tags = models.Tag.objects.filter(name__startswith=startswith)
    taglist = [ tag.name for tag in tags  ]
    return JsonResponse({"tags":taglist})