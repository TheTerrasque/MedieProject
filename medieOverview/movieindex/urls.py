from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MoviesIndex.as_view(), name="movie-list"),
    url(r'^thumb/([0-9]+)/$', views.display_image, name="thumb-show"),
    url(r'^play/([0-9]+)/$', views.play_movie, name="movie-play"),
    url(r'^mf/$', views.MFolderIndex.as_view(), name="moviefolder-list"),
    url(r'^mf/([0-9]+)/scan/$', views.scan_moviefolder, name="moviefolder-scan"),
    #url(r'^articles/([0-9]{4})/([0-9]{2})/$', views.month_archive),
    #url(r'^articles/([0-9]{4})/([0-9]{2})/([0-9]+)/$', views.article_detail),
]