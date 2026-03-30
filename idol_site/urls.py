from django.contrib import admin
from django.urls import path
from wiki import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),

    # 首页
    path('', views.index, name='home'),

    # 成员详情
    path('member/<int:pk>/', views.member_detail, name='member_detail'),

    # 官方物料系列页
    path('media-series/<int:pk>/', views.media_series_detail, name='media_series_detail'),

# 相册页
    path('gallery/', views.gallery_view, name='gallery'),
    
]


# ✅ 正确的 media 映射（只追加，不覆盖）
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
