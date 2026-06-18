from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('menus', views.MenuItemViewSet)
router.register('articles', views.ArticleViewSet)
router.register('banners', views.BannerViewSet)
router.register('media', views.MediaFileViewSet)
router.register('contacts', views.ContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Auth
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/me/', views.me_view, name='me'),
    path('auth/change-password/', views.change_password, name='change-password'),
    # Settings & Stats
    path('settings/', views.site_settings, name='settings'),
    path('dashboard/', views.dashboard_stats, name='dashboard'),
]
