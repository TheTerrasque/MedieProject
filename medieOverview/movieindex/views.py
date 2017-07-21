import datetime
import os
from mimetypes import MimeTypes

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView

from ranged_fileresponse import RangedFileResponse

from . import models, scanner
from .forms import MovieFilterForm

from django.core import serializers

@login_required
def display_image(request, imageid):
    thumb = models.Thumb.objects.get(id=imageid)
    r = HttpResponse(thumb.image, content_type="image/jpeg")
    r["Cache-Control"] = "max-age=31536000"
    return r

@csrf_exempt
@permission_required("movieindex.tag_movie")
def tagMovie(request, pk):
    movies = []
    for pkp in pk.split(","):
        movie = models.Movie.objects.get(id=pkp)
        if not movie.user_access(request.user): return HttpResponse("BAD")
        movies.append(movie)
    tag = request.POST.get("tag")
    with models.transaction.atomic():
        for movie in movies:
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
        "download_url": movie.get_download_url(),
    }
    return JsonResponse(d)
    
class MFolderIndex(LoginRequiredMixin, ListView):
    model = models.MovieFolder

class MovieStreamPlay(LoginRequiredMixin, DetailView):
    model = models.Movie
    template_name = "movieindex/movie_stream_play.html"

    def get_queryset(self):
        mcs = [
            x for x in models.MovieCategory.objects.all()
            if x.user_access(self.request.user)
            ]
        Q = models.Movie.objects.filter(category__in=mcs)
        return Q

    def get_context_data(self, **kwargs):
        context = super(MovieStreamPlay, self).get_context_data(**kwargs)
        context['baseurl'] = '{scheme}://{host}'.format(scheme=self.request.scheme,
                                                           host=self.request.get_host())
        return context

class MoviesIndex(LoginRequiredMixin, ListView):
    model = models.Movie
    paginate_by = 100
    context_object_name = 'movies'
    
    def get_queryset(self):
        self.form = MovieFilterForm(self.request.GET)
        if self.form.is_valid():
            formdata = self.form.cleaned_data
            self.paginate_by = formdata.get("perpage")
        else:
            self.form = MovieFilterForm()
            formdata = {}

        query = formdata.get('query')

        mcs = [
            x for x in models.MovieCategory.objects.all()
            if x.user_access(self.request.user)
            ]
        Q = models.Movie.objects.filter(category__in=mcs)

        if query:
            Q = Q.filter(subpath__icontains=query)
        
        if formdata.get('notags'):
            Q = Q.filter(tags=None)
        else:
            for tag in self.get_tags():
                Q = Q.filter(tags__id = tag)
        return Q
    
    def get_tags(self):
        t = self.request.GET.getlist("tag", [])
        r = [int(tn) for tn in t]
        return r
    
    def get_context_data(self, **kwargs):
        context = super(MoviesIndex, self).get_context_data(**kwargs)
        ct = models.Tag.objects.filter(id__in=self.get_tags())
        context['ctags'] = ct
        context['form'] = self.form
        context['baseurl'] = '{scheme}://{host}'.format(scheme=self.request.scheme,
                                                    host=self.request.get_host())
        context['tags'] = models.Tag.objects.filter(movies__in=self.get_queryset()).distinct()
        return context
   
def download_movie_key(request, movieid):
    print "Got movie req"
    movie = models.Movie.objects.get(id=movieid)
    key = request.GET.get("key")
    if key and movie.check_dl_key(key):
        return dl_movie_Helper(request, movie)


def dl_movie_Helper(request, movie):
    if not movie.user_access(request.user): return "BAD"
    filename = movie.get_path()
    mime = MimeTypes().guess_type(filename)[0]
    fr = RangedFileResponse(request, filename, content_type=mime)
    fr['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(filename)
    if fr.status_code == 200:
        movie.log("Downloaded movie")
    return fr

@permission_required("movieindex.download_movie")    
def download_movie(request, movieid):
    movie = models.Movie.objects.get(id=movieid)
    return dl_movie_Helper(request, movie)

@permission_required("movieindex.play_movie")    
def play_movie(request, movieid):
    movie = models.Movie.objects.get(id=movieid)
    if not movie.user_access(request.user): return "BAD"
    movie.play_file()
    movie.log("Played movie")
    return HttpResponse("OK")

@permission_required("movieindex.scan_folder")
def progress_scan_moviefolder(request):
    mfid = request.GET.get("mfid")
    r = models.WorkerCommand.objects.filter(task="SCANFOLDER", target=mfid).exclude(status__in=( "DONE")).order_by("-id")
    if r:
        return JsonResponse({
            "status": r[0].status,
            "progress": r[0].progress
        }, safe=False)
    return JsonResponse({
        "status": "",
        "progress": "No work queued"
    }, safe=False)

@permission_required("movieindex.scan_folder")
def scan_moviefolder(request, mfid):
    models.WorkerCommand.objects.create(task="SCANFOLDER", target=mfid)
    return redirect('moviefolder-list')
    mf = models.MovieFolder.objects.get(id=mfid)
    c = mf.default_category
    mf.last_scanned = datetime.datetime.now()
    mf.save()
    
    def iter_response():
        yield u"<div>Scanning folder '%s'...</div><br/>" % mf.name
        yield u"<table class='list'>"
        yield u"<tr><td>%s</td> <td>%s</d> <td>%s</td></tr>" % ("Folder", "File", "Status")
        for root, f, status in scanner.scan(mf, c):
            if status != "Skipped" or request.GET.get("showskip"):
                root = root[:-len(f)]
                yield u"<tr><td>%s</td> <td>%s</d> <td>%s</td></tr>" % (root, f, status)
        yield u"</table>Scan done"
        
    return StreamingHttpResponse(iter_response())

@permission_required("movieindex.tag_movie")
def json_tags(request):
    startswith = request.GET.get("text")
    tags = models.Tag.objects.filter(name__startswith=startswith)
    taglist = [ tag.name for tag in tags  ]
    return JsonResponse({"tags":taglist})
