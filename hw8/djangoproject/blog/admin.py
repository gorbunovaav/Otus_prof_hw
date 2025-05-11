from django.contrib import admin
from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish_date', 'status']
    list_filter = ['created_date', 'publish_date', 'status']
    search_fields =['title', 'body']
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'publish_date'
    ordering = ['publish_date', 'author']
    raw_id_fields = ['author']

admin.site.register(Post, PostAdmin)