from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "description", "genre", "year", "cover"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "cover": forms.FileInput(attrs={"accept": "image/jpeg,image/png,image/webp"}),
        }
        help_texts = {"cover": "JPEG, PNG или WebP, до 5 МБ. Поле необязательно."}

    def clean_cover(self):
        cover = self.cleaned_data.get("cover")
        if cover:
            if cover.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Размер обложки не должен превышать 5 МБ.")
            if getattr(cover, "image", None) and cover.image.format not in {"JPEG", "PNG", "WEBP"}:
                raise forms.ValidationError("Выберите изображение JPEG, PNG или WebP.")
        return cover
