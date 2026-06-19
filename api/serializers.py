from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Article, ArticleImage, Banner, MediaFile, Contact, SiteSettings
import re


def generate_slug(title, Model):
    base = re.sub(r'[^\w\s-]', '', title.lower())
    base = re.sub(r'[\s_]+', '-', base).strip('-')
    slug = base
    n = 1
    while Model.objects.filter(slug=slug).exists():
        slug = f"{base}-{n}"
        n += 1
    return slug


# ── AUTH ──
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)


# ── MENU ──
class MenuItemChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'slug', 'order', 'is_active']


class MenuItemSerializer(serializers.ModelSerializer):
    # The model field is required (no blank=True), which made DRF treat
    # "slug" as a mandatory input — fine for the admin panel (which fills it
    # in via JS as you type the title), but fragile for any other client.
    # Making it optional here and auto-generating when missing/blank keeps
    # the existing generate_slug() helper actually reachable.
    slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True, max_length=50)
    children = MenuItemChildSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'slug', 'parent', 'order', 'is_active', 'children', 'created_at']

    def create(self, validated_data):
        if not validated_data.get('slug'):
            validated_data['slug'] = generate_slug(validated_data['title'], MenuItem)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'slug' in validated_data and not validated_data.get('slug'):
            validated_data['slug'] = generate_slug(validated_data.get('title', instance.title), MenuItem)
        return super().update(instance, validated_data)


# ── ARTICLE IMAGE ──
class ArticleImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ArticleImage
        fields = ['id', 'image', 'image_url', 'caption', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ── ARTICLE ──
class ArticleListSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    menu_title = serializers.CharField(source='menu.title', read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'status',
            'cover_image_url', 'intro', 'menu_title',
            'author_name', 'views', 'is_featured',
            'published_at', 'created_at'
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None


class ArticleDetailSerializer(serializers.ModelSerializer):
    # The admin panel never sends a "slug" field when creating an article
    # (there's no input for it), but the model's SlugField has no blank=True,
    # so DRF was treating it as required and rejecting every new article
    # before create() got a chance to auto-generate one. Making it optional
    # here lets generate_slug() actually do its job.
    slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True, max_length=500)
    cover_image_url = serializers.SerializerMethodField()
    images = ArticleImageSerializer(many=True, read_only=True)
    menu_title = serializers.CharField(source='menu.title', read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'status',
            'cover_image', 'cover_image_url', 'intro', 'body',
            'menu', 'menu_title', 'author_name',
            'views', 'is_featured', 'published_at',
            'created_at', 'updated_at', 'images'
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if obj.cover_image and request:
            return request.build_absolute_uri(obj.cover_image.url)
        return None

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return None

    def create(self, validated_data):
        if not validated_data.get('slug'):
            validated_data['slug'] = generate_slug(validated_data['title'], Article)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'slug' in validated_data and not validated_data.get('slug'):
            validated_data['slug'] = generate_slug(validated_data.get('title', instance.title), Article)
        return super().update(instance, validated_data)


# ── BANNER ──
class BannerSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Banner
        fields = ['id', 'title', 'subtitle', 'image', 'image_url', 'link', 'order', 'is_active', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


# ── MEDIA FILE ──
class MediaFileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = ['id', 'name', 'file', 'file_url', 'file_type', 'size', 'created_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


# ── CONTACT ──
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'full_name', 'phone', 'email', 'subject', 'message', 'status', 'note', 'created_at']
        read_only_fields = ['status', 'note', 'created_at']


class ContactAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


# ── SITE SETTINGS ──
class SiteSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = '__all__'

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None
