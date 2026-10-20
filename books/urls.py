from django.urls import path
from . import views
app_name = "books"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("books/", views.BookListView.as_view(), name="list"),
    path("books/add/", views.BookCreateView.as_view(), name="add"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="detail"),
]
