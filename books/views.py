from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from .forms import BookForm
from .models import Book

class HomeView(TemplateView):
    template_name = "books/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(featured_books=Book.objects.all()[:4], book_count=Book.objects.count())
        return context

class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 8

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        genre = self.request.GET.get("genre", "")
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(author__icontains=query))
        if genre:
            queryset = queryset.filter(genre=genre)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(genres=Book.Genre.choices, query=self.request.GET.get("q", ""),
                       selected_genre=self.request.GET.get("genre", ""), filter_params=params.urlencode())
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_form.html"

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        messages.success(self.request, "Книга добавлена в библиотеку.")
        return super().form_valid(form)
