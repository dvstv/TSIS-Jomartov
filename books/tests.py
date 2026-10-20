from io import BytesIO, StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image
from .forms import BookForm
from .models import Book


def cover_file(format="PNG"):
    stream = BytesIO()
    Image.new("RGB", (30, 40), "green").save(stream, format=format)
    return SimpleUploadedFile("cover." + format.lower(), stream.getvalue(), content_type="image/" + format.lower())


class LibraryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("reader", password="ReaderPass!739")
        cls.book = Book.objects.create(title="Космос", author="Карл Саган", description="О Вселенной", year=1980, genre="science")

    def test_home_catalog_and_detail(self):
        for url in [reverse("books:home"), reverse("books:list"), self.book.get_absolute_url()]:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, self.book.title)
            self.assertTemplateUsed(response, "base.html")
        self.assertContains(self.client.get(self.book.get_absolute_url()), "О Вселенной")

    def test_search_and_genre_filter(self):
        Book.objects.create(title="Хоббит", author="Толкин", description="Приключение", year=1937, genre="adventure")
        response = self.client.get(reverse("books:list"), {"q": "Саган", "genre": "science"})
        self.assertContains(response, "Космос")
        self.assertNotContains(response, "Хоббит")
        response = self.client.get(reverse("books:list"), {"q": "несуществующая книга"})
        self.assertContains(response, "Книги не найдены")

    def test_pagination_preserves_filters(self):
        for number in range(10):
            Book.objects.create(title=f"Space {number}", author="Author", description="Description", year=2000, genre="science")
        response = self.client.get(reverse("books:list"), {"q": "Space", "genre": "science"})
        self.assertEqual(len(response.context["books"]), 8)
        self.assertContains(response, "q=Space&amp;genre=science&amp;page=2")
        response = self.client.get(reverse("books:list"), {"q": "Space", "genre": "science", "page": 2})
        self.assertEqual(len(response.context["books"]), 2)

    def test_missing_book_returns_404(self):
        self.assertEqual(self.client.get(reverse("books:detail", args=[99999])).status_code, 404)

    def test_anonymous_cannot_add_book(self):
        response = self.client.post(reverse("books:add"), {"title": "Forbidden"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)
        self.assertEqual(Book.objects.count(), 1)

    def test_create_book_upload_and_render_media(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            self.client.force_login(self.user)
            response = self.client.post(reverse("books:add"), {
                "title": "Новая книга", "author": "Автор", "description": "Описание",
                "genre": "classic", "year": 2020, "cover": cover_file(),
            })
            book = Book.objects.get(title="Новая книга")
            self.assertRedirects(response, book.get_absolute_url())
            self.assertEqual(book.added_by, self.user)
            self.assertTrue(Path(book.cover.path).is_file())
            self.assertTrue(book.cover.url.startswith("/media/covers/"))
            self.assertContains(self.client.get(book.get_absolute_url()), book.cover.url)

    def test_server_validation_rejects_invalid_image_and_fields(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("books:add"), {
            "title": "Invalid", "author": "Author", "description": "Description", "genre": "science", "year": 0,
            "cover": SimpleUploadedFile("fake.png", b"not an image", content_type="image/png"),
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("year", response.context["form"].errors)
        self.assertIn("cover", response.context["form"].errors)
        self.assertFalse(Book.objects.filter(title="Invalid").exists())

    def test_cover_size_and_format_limits(self):
        fields = {"title": "Title", "author": "Author", "description": "Description", "genre": "classic", "year": 2020}
        large = cover_file()
        large.size = 5 * 1024 * 1024 + 1
        form = BookForm(fields, {"cover": large})
        self.assertFalse(form.is_valid())
        self.assertIn("cover", form.errors)
        form = BookForm(fields, {"cover": cover_file("GIF")})
        self.assertFalse(form.is_valid())
        self.assertIn("cover", form.errors)

    def test_csrf_required_for_upload(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post(reverse("books:add"), {}).status_code, 403)

    def test_user_content_is_escaped(self):
        self.book.title = '<script>alert("xss")</script>'
        self.book.save()
        response = self.client.get(self.book.get_absolute_url())
        self.assertNotContains(response, self.book.title)
        self.assertContains(response, "&lt;script&gt;")

    def test_demo_command_is_repeatable_and_creates_real_images(self):
        with TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            output = StringIO()
            call_command("seed_demo", stdout=output)
            count = Book.objects.count()
            call_command("seed_demo", stdout=output)
            self.assertEqual(Book.objects.count(), count)
            self.assertEqual(count, 10)
            for book in Book.objects.all():
                with Image.open(book.cover.path) as image:
                    image.verify()
