from django.contrib import admin
from . import models
# Register your models here.

@admin.register(models.MovieLog)
class MovieLogAdmin(admin.ModelAdmin):
    list_display = ["movie", "user", "entry"]
    search_fields = ["movie__title", "user__username", "entry"]
    list_filter = ["user"]
    #date_hierarchy = "added"

@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "folder", "category"]
    list_filter = ["folder", "category"]
    search_fields = ["title", "subpath"]
    raw_id_fields = ["main_thumb"]
    filter_horizontal = ["tags"]
    fieldsets = (
        (None, {"fields": ["title", "category", "tags"]}),
        ("Filedata", {"fields": ["folder", "subpath", "rating", "length", "size", "bitrate", "codec", "fps", "height", "width", "main_thumb", "metadata"]}),
    )
    #date_hierarchy = "added"
    
admin.site.register(models.MovieCategory)
admin.site.register(models.MovieFolder)
admin.site.register(models.Tag)
admin.site.register(models.WorkerCommand)
admin.site.register(models.Thumb)