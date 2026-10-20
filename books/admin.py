from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "genre", "year", "added_by"]
    list_filter = ["genre", "year"]
    search_fields = ["title", "author"]
