from django.contrib import admin
from .models import MenuItem, Article, ArticleImage, Banner, MediaFile, Contact, SiteSettings


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'parent', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('title',)}


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'status', 'menu', 'views', 'is_featured', 'created_at']
    list_filter = ['status', 'category', 'is_featured']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleImageInline]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_type', 'size', 'created_at']
    list_filter = ['file_type']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'subject', 'status', 'created_at']
    list_filter = ['status']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    pass
