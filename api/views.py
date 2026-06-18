from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from .models import MenuItem, Article, ArticleImage, Banner, MediaFile, Contact, SiteSettings
from .serializers import (
    MenuItemSerializer, ArticleListSerializer, ArticleDetailSerializer,
    ArticleImageSerializer, BannerSerializer, MediaFileSerializer,
    ContactSerializer, ContactAdminSerializer, SiteSettingsSerializer,
    UserSerializer, ChangePasswordSerializer
)


# ══════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Login yoki parol noto\'g\'ri'}, status=400)
    if not user.is_staff:
        return Response({'error': 'Admin huquqi yo\'q'}, status=403)
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
    except Exception:
        pass
    return Response({'message': 'Chiqildi'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    s = ChangePasswordSerializer(data=request.data)
    if not s.is_valid():
        return Response(s.errors, status=400)
    if not request.user.check_password(s.validated_data['old_password']):
        return Response({'error': 'Eski parol noto\'g\'ri'}, status=400)
    request.user.set_password(s.validated_data['new_password'])
    request.user.save()
    return Response({'message': 'Parol o\'zgartirildi'})


# ══════════════════════════════════════════════
#  MENU
# ══════════════════════════════════════════════
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filterset_fields = ['is_active', 'parent']
    search_fields = ['title', 'slug']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'tree']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Faqat top-level menyu (bola-larni nested qaytaradi)"""
        roots = MenuItem.objects.filter(parent=None, is_active=True)
        return Response(MenuItemSerializer(roots, many=True, context={'request': request}).data)


# ══════════════════════════════════════════════
#  ARTICLE
# ══════════════════════════════════════════════
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    filterset_fields = ['category', 'status', 'menu', 'is_featured']
    search_fields = ['title', 'intro', 'body']
    ordering_fields = ['created_at', 'views', 'published_at']
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'tree']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Article.objects.all()
        if not (self.request.user and self.request.user.is_authenticated):
            qs = qs.filter(status='published')
        return qs

    def perform_create(self, serializer):
        article = serializer.save(author=self.request.user)
        if article.status == 'published' and not article.published_at:
            article.published_at = timezone.now()
            article.save()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated:
            instance.views += 1
            instance.save(update_fields=['views'])
        return Response(ArticleDetailSerializer(instance, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def publish(self, request, pk=None):
        article = self.get_object()
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        return Response({'message': 'Maqola chop etildi'})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_image(self, request, pk=None):
        article = self.get_object()
        images = request.FILES.getlist('images')
        created = []
        for img in images:
            obj = ArticleImage.objects.create(
                article=article,
                image=img,
                caption=request.data.get('caption', ''),
            )
            created.append(ArticleImageSerializer(obj, context={'request': request}).data)
        return Response(created, status=201)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        qs = Article.objects.filter(status='published', is_featured=True)[:6]
        return Response(ArticleListSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def by_menu(self, request):
        menu_slug = request.query_params.get('slug')
        if not menu_slug:
            return Response({'error': 'slug parametri kerak'}, status=400)
        qs = Article.objects.filter(menu__slug=menu_slug, status='published')
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                ArticleListSerializer(page, many=True, context={'request': request}).data
            )
        return Response(ArticleListSerializer(qs, many=True, context={'request': request}).data)


# ══════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════
class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve','tree']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return Banner.objects.all()
        return Banner.objects.filter(is_active=True)


# ══════════════════════════════════════════════
#  MEDIA FILES
# ══════════════════════════════════════════════
class MediaFileViewSet(viewsets.ModelViewSet):
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ['file_type']
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'tree']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        f = self.request.FILES.get('file')
        size = f.size if f else 0
        # Detect type
        name = f.name.lower() if f else ''
        if name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
            ftype = 'image'
        elif name.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
            ftype = 'document'
        else:
            ftype = 'other'
        serializer.save(uploaded_by=self.request.user, size=size, file_type=ftype)


# ══════════════════════════════════════════════
#  CONTACT
# ══════════════════════════════════════════════
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    filterset_fields = ['status']
    search_fields = ['full_name', 'phone', 'subject']

    def get_serializer_class(self):
        if self.request.user and self.request.user.is_authenticated:
            return ContactAdminSerializer
        return ContactSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def set_status(self, request, pk=None):
        contact = self.get_object()
        contact.status = request.data.get('status', contact.status)
        contact.note = request.data.get('note', contact.note)
        contact.save()
        return Response(ContactAdminSerializer(contact).data)


# ══════════════════════════════════════════════
#  SITE SETTINGS
# ══════════════════════════════════════════════
@api_view(['GET', 'PUT', 'PATCH'])
def site_settings(request):
    obj, _ = SiteSettings.objects.get_or_create(pk=1)
    if request.method == 'GET':
        return Response(SiteSettingsSerializer(obj, context={'request': request}).data)
    if not request.user.is_authenticated:
        return Response({'error': 'Ruxsat yo\'q'}, status=403)
    s = SiteSettingsSerializer(obj, data=request.data, partial=True, context={'request': request})
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


# ══════════════════════════════════════════════
#  DASHBOARD STATS
# ══════════════════════════════════════════════
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    return Response({
        'articles': {
            'total': Article.objects.count(),
            'published': Article.objects.filter(status='published').count(),
            'draft': Article.objects.filter(status='draft').count(),
        },
        'menus': MenuItem.objects.count(),
        'banners': Banner.objects.count(),
        'contacts': {
            'total': Contact.objects.count(),
            'new': Contact.objects.filter(status='new').count(),
        },
        'media': MediaFile.objects.count(),
    })
