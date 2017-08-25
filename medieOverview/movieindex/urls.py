from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MoviesIndex.as_view(), name="movie-list"),
    url(r'^help/$', views.HelpPage.as_view(), name="movie-help"),
    url(r'^tags/(?P<tags>[0-9,]+)/$', views.MoviesIndex.as_view(), name="movie-list-tag"),
    url(r'^tags/startswith/$', views.json_tags, name="movie-json-tags"),
    url(r'^thumb/([0-9]+)/$', views.display_image, name="thumb-show"),
    url(r'^movie/([0-9]+)/play/$', views.play_movie, name="movie-play"),
    url(r'^movie/(?P<pk>[0-9]+)/stream/$', views.MovieStreamPlay.as_view(), name="movie-stream"),
    url(r'^movie/([0-9]+)/download/$', views.download_movie, name="movie-download"),
    url(r'^movie/([0-9]+)/download_key/$', views.download_movie_key, name="movie-download-key"),
    url(r'^mf/$', views.MFolderIndex.as_view(), name="moviefolder-list"),
    url(r'^movie/(?P<pk>[0-9]+)/json/$', views.jsonMovie, name="movie-json-detail"),
    url(r'^movie/(?P<pk>[0-9,]+)/addtag/$', views.tagMovie, name="movie-addtag"),
    url(r'^mf/([0-9]+)/scan/$', views.scan_moviefolder, name="moviefolder-scan"),
    url(r'^mf/status/$', views.progress_scan_moviefolder, name="moviefolder-scan-status"),
    #url(r'^articles/([0-9]{4})/([0-9]{2})/$', views.month_archive),
    #url(r'^articles/([0-9]{4})/([0-9]{2})/([0-9]+)/$', views.article_detail),
]