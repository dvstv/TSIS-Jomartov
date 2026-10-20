from io import BytesIO
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont
from books.models import Book

BOOKS = [
    ("Абай жолы", "Мухтар Ауэзов", 1942, "classic", "Роман-эпопея о жизни Абая Кунанбаева, культуре и традициях казахского народа.", "#244b46"),
    ("Маленький принц", "Антуан де Сент-Экзюпери", 1943, "fiction", "Философская сказка о дружбе, ответственности и умении видеть сердцем.", "#b6673f"),
    ("Двадцать тысяч лье под водой", "Жюль Верн", 1870, "adventure", "Путешествие на подводном корабле «Наутилус» с загадочным капитаном Немо.", "#325b76"),
    ("Краткая история времени", "Стивен Хокинг", 1988, "science", "Знакомство с пространством, временем, чёрными дырами и устройством Вселенной.", "#474264"),
    ("Гордость и предубеждение", "Джейн Остин", 1813, "classic", "История Элизабет Беннет: о выборе, чувствах и первом впечатлении.", "#76514f"),
    ("Хоббит", "Джон Р. Р. Толкин", 1937, "adventure", "Бильбо Бэггинс отправляется в неожиданное путешествие к Одинокой горе.", "#51613f"),
    ("Человек-амфибия", "Александр Беляев", 1928, "fiction", "История Ихтиандра, способного жить под водой, и его встречи с миром людей.", "#2b6b70"),
    ("Космос", "Карл Саган", 1980, "science", "Научно-популярное путешествие по Вселенной: от истории астрономии до поиска жизни за пределами Земли.", "#916b39"),
    ("Остров сокровищ", "Роберт Льюис Стивенсон", 1883, "adventure", "Карта, морское путешествие и поиски сокровищ глазами юного Джима Хокинса.", "#764434"),
    ("Слова назидания", "Абай Кунанбаев", 1890, "classic", "Размышления поэта о знаниях, труде, нравственности и человеческом достоинстве.", "#4c5348"),
]

class Command(BaseCommand):
    help = "Создать демонстрационные книги и обложки; повторный запуск не дублирует записи."

    def handle(self, *args, **options):
        count = 0
        for index, (title, author, year, genre, description, color) in enumerate(BOOKS, 1):
            book, created = Book.objects.get_or_create(title=title, author=author, defaults={
                "year": year, "genre": genre, "description": description,
            })
            if created:
                count += 1
            if not book.cover:
                image = Image.new("RGB", (600, 840), color)
                draw = ImageDraw.Draw(image)
                draw.rectangle((30, 30, 570, 810), outline="#e4d8b7", width=3)
                draw.ellipse((180, 190, 420, 430), outline="#e4d8b7", width=4)
                draw.line((300, 190, 300, 430), fill="#e4d8b7", width=3)
                draw.line((180, 310, 420, 310), fill="#e4d8b7", width=3)
                # Default Pillow font is bundled, so no system fonts are required.
                font = ImageFont.load_default(size=38)
                draw.text((90, 530), "OPEN LIBRARY", font=font, fill="#fff4dc")
                draw.text((90, 600), f"COLLECTION / {index:02d}", font=ImageFont.load_default(size=23), fill="#e4d8b7")
                output = BytesIO()
                image.save(output, format="PNG")
                book.cover.save(f"demo-{index}.png", ContentFile(output.getvalue()), save=True)
        self.stdout.write(self.style.SUCCESS(f"Добавлено книг: {count}. Всего: {Book.objects.count()}."))
