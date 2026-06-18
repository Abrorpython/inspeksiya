from django.db import models
from django.contrib.auth.models import User


class MenuItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Nom")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.CASCADE, related_name='children',
        verbose_name="Ota-menyu"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Menyu elementi"
        verbose_name_plural = "Menyu elementlari"
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Qoralama'),
        ('published', 'Chop etilgan'),
        ('archived', 'Arxivlangan'),
    ]
    CATEGORY_CHOICES = [
        ('news', 'Yangiliklar'),
        ('announcement', "E'lonlar"),
        ('regulation', 'Qonunchilik'),
        ('report', 'Hisobotlar'),
        ('other', 'Boshqa'),
    ]

    menu = models.ForeignKey(
        MenuItem, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='articles', verbose_name="Menyu bo'limi"
    )
    title = models.CharField(max_length=500, verbose_name="Sarlavha")
    slug = models.SlugField(unique=True, max_length=500, verbose_name="Slug")
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES,
        default='news', verbose_name="Kategoriya"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='draft', verbose_name="Holat"
    )
    cover_image = models.ImageField(
        upload_to='images/articles/',
        null=True, blank=True,
        verbose_name="Muqova rasmi"
    )
    intro = models.TextField(blank=True, verbose_name="Qisqa mazmun")
    body = models.TextField(verbose_name="Maqola matni")
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, verbose_name="Muallif"
    )
    views = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar")
    is_featured = models.BooleanField(default=False, verbose_name="Tanlangan")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Maqola"
        verbose_name_plural = "Maqolalar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='images/gallery/')
    caption = models.CharField(max_length=300, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.article.title} - rasm {self.id}"


class Banner(models.Model):
    title = models.CharField(max_length=300, verbose_name="Sarlavha")
    subtitle = models.TextField(blank=True, verbose_name="Qo'shimcha matn")
    image = models.ImageField(upload_to='images/banners/', verbose_name="Rasm")
    link = models.URLField(blank=True, verbose_name="Havola")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlar"
        ordering = ['order']

    def __str__(self):
        return self.title


class MediaFile(models.Model):
    FILE_TYPES = [
        ('image', 'Rasm'),
        ('document', 'Hujjat'),
        ('other', 'Boshqa'),
    ]
    name = models.CharField(max_length=300, verbose_name="Nomi")
    file = models.FileField(upload_to='files/', verbose_name="Fayl")
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='image')
    size = models.PositiveIntegerField(default=0, verbose_name="Hajm (bayt)")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fayl"
        verbose_name_plural = "Fayllar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Contact(models.Model):
    STATUS = [
        ('new', 'Yangi'),
        ('in_progress', "Ko'rib chiqilmoqda"),
        ('done', 'Hal etildi'),
    ]
    full_name = models.CharField(max_length=200, verbose_name="Ism Familiya")
    phone = models.CharField(max_length=30, verbose_name="Telefon")
    email = models.EmailField(blank=True, verbose_name="Elektron pochta")
    subject = models.CharField(max_length=300, verbose_name="Mavzu")
    message = models.TextField(verbose_name="Xabar")
    status = models.CharField(max_length=20, choices=STATUS, default='new')
    note = models.TextField(blank=True, verbose_name="Admin izohi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Murojaat"
        verbose_name_plural = "Murojaatlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class SiteSettings(models.Model):
    site_name = models.CharField(
        max_length=300,
        default="Nazorat Qilish Inspeksiyasi"
    )
    tagline = models.CharField(max_length=500, blank=True)
    logo = models.ImageField(
        upload_to='images/site/', null=True, blank=True
    )
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    working_hours = models.CharField(max_length=200, blank=True)
    telegram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    footer_text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sayt sozlamalari"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton
        super().save(*args, **kwargs)