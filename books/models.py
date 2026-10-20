from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

class Book(models.Model):
    class Genre(models.TextChoices):
        CLASSIC = "classic", "Классика"
        FICTION = "fiction", "Фантастика"
        ADVENTURE = "adventure", "Приключения"
        SCIENCE = "science", "Наука"
        OTHER = "other", "Другое"

    title = models.CharField("Название", max_length=200)
    author = models.CharField("Автор", max_length=160)
    description = models.TextField("Описание", max_length=10000)
    genre = models.CharField("Жанр", max_length=20, choices=Genre.choices, default=Genre.OTHER)
    year = models.PositiveSmallIntegerField("Год издания", validators=[MinValueValidator(1), MaxValueValidator(2100)])
    cover = models.ImageField("Обложка", upload_to="covers/%Y/%m/", blank=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="Добавил", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return f"{self.title} — {self.author}"

    def get_absolute_url(self):
        return reverse("books:detail", args=[self.pk])
