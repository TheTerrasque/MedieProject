from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "folder", "category"]
    list_filter = ["folder", "category"]
    search_fields = ["title", "subpath"]
    raw_id_fields = ["main_thumb"]
    filter_horizontal = ["tags"]
    
admin.site.register(models.MovieCategory)
admin.site.register(models.MovieFolder)
admin.site.register(models.Tag)
admin.site.register(models.Thumb)