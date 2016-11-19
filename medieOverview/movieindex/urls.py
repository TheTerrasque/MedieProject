from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.MoviesIndex.as_view()),
    url(r'^thumb/([0-9]+)/$', views.display_image, name="thumb-show"),
    #url(r'^articles/([0-9]{4})/([0-9]{2})/$', views.month_archive),
    #url(r'^articles/([0-9]{4})/([0-9]{2})/([0-9]+)/$', views.article_detail),
]