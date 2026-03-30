from django.contrib import admin
from django.utils.html import format_html

from .models import (
    IdolGroup, Member, Album, Song,
    MemberSelfIntro, MemberGallery, MemberFancam,
    MediaSeries, OfficialMedia,
    Event, Photo,Schedule,ChinaSocialAccount,FanStation,FanReaction, FanOOTD,FanPhotoFeature
)


# =====================================================
# 1. 后台标题设置
# =====================================================
admin.site.site_header = "Pickus 官方百科后台"
admin.site.site_title = "Pickus Fan Site"
admin.site.index_title = "欢迎来到 Pickus 偶像数据管理系统"


# =====================================================
# 2. 成员页面内联模块
# 在编辑单个成员时，直接在成员页里添加这些内容
# =====================================================

# 成员自述图内联
class SelfIntroInline(admin.StackedInline):
    model = MemberSelfIntro
    extra = 1
    verbose_name = "成员自述图片"
    verbose_name_plural = "成员自述图片集"


# 成员个人相册内联
class GalleryInline(admin.TabularInline):
    model = MemberGallery
    extra = 3
    verbose_name = "相册照片"
    verbose_name_plural = "个人相册"


# 成员直拍内联
class FancamInline(admin.StackedInline):
    model = MemberFancam
    extra = 1
    verbose_name = "直拍视频"
    verbose_name_plural = "精彩直拍视频流"


# =====================================================
# 3. 成员管理
# =====================================================
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('stage_name', 'show_photo', 'group', 'position', 'birthday')
    list_filter = ('group',)

    # 在成员编辑页中嵌入三个板块
    inlines = [SelfIntroInline, GalleryInline, FancamInline]

    # 后台列表页显示头像缩略图
    def show_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;border-radius:50%;" />',
                obj.photo.url
            )
        return "暂无头像"

    show_photo.short_description = "头像预览"


# =====================================================
# 4. 团体管理
# =====================================================
@admin.register(IdolGroup)
class IdolGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'debut_date', 'company')


# =====================================================
# 5. 歌曲内联（嵌入专辑页）
# =====================================================
class SongInline(admin.TabularInline):
    model = Song
    extra = 3


# =====================================================
# 6. 专辑管理
# =====================================================
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'release_date', 'music_url')

    # 控制后台编辑页字段顺序
    fields = (
        'group',
        'title',
        'cover',
        'release_date',
        'music_url',
        'preview_audio',
        'preview_start',
        'preview_duration',
    )

    # 在专辑页直接管理歌曲
    inlines = [SongInline]


# =====================================================
# 7. 官方物料单集内联
# =====================================================
class OfficialMediaInline(admin.TabularInline):
    model = OfficialMedia
    extra = 1
    verbose_name = "单集内容"
    verbose_name_plural = "系列下的所有单集"


# =====================================================
# 8. 官方物料系列管理
# =====================================================
@admin.register(MediaSeries)
class MediaSeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'category', 'sort_order')
    list_filter = ('group', 'category')
    search_fields = ('title',)
    ordering = ('category', 'sort_order', 'id')

    # 在系列页直接管理单集
    inlines = [OfficialMediaInline]


# =====================================================
# 9. 官方物料单集管理
# =====================================================
@admin.register(OfficialMedia)
class OfficialMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'series', 'release_date', 'sort_order')
    list_filter = ('series__category', 'series')
    search_fields = ('title', 'series__title')
    ordering = ('series', 'sort_order', '-release_date')


# =====================================================
# 10. 活动管理（新相册系统）
# =====================================================
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'event_type', 'date')
    list_filter = ('group', 'event_type')
    search_fields = ('title', 'description')
    ordering = ('-date', '-id')


# =====================================================
# 11. 活动图片管理（单张上传版）
# 这里先不做批量上传，优先保证后台稳定
# =====================================================
@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'created_at')
    list_filter = ('event', 'event__group')
    search_fields = ('caption', 'event__title')

    # 多对多成员字段使用横向选择器，体验更好
    filter_horizontal = ('members',)

    ordering = ('-id',)


    # =====================================================
# 12. 团体行程管理（Schedule）
# 后续用于首页时间轴和世界地图
# =====================================================
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'date', 'city', 'country', 'schedule_type', 'status')
    list_filter = ('group', 'schedule_type', 'status', 'country')
    search_fields = ('title', 'city', 'country', 'venue')
    ordering = ('date', 'sort_order', 'id')

    # 后台编辑页字段顺序
    fields = (
        'group',
        'title',
        'date',
        'city',
        'country',
        'venue',
        'schedule_type',
        'status',
        'latitude',
        'longitude',
        'description',
        'sort_order',
    )

    # =====================================================
# 13. 中国平台账号管理
# =====================================================
@admin.register(ChinaSocialAccount)
class ChinaSocialAccountAdmin(admin.ModelAdmin):
    list_display = ('platform', 'account_name', 'group', 'sort_order')
    list_filter = ('group', 'platform')
    search_fields = ('account_name',)
    ordering = ('sort_order', 'id')


# =====================================================
# 14. 摆摊区站子管理
# =====================================================
@admin.register(FanStation)
class FanStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'group', 'weibo_name', 'sort_order')
    list_filter = ('group',)
    search_fields = ('name', 'weibo_name', 'description')
    ordering = ('sort_order', 'id')



# =====================================================
# 15. 烧烤一下管理
# =====================================================
@admin.register(FanReaction)
class FanReactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'group', 'sort_order')
    list_filter = ('group', 'category')
    search_fields = ('title', 'summary')
    ordering = ('sort_order', 'id')



# =====================================================
# 16. 今日出炉管理
# =====================================================
@admin.register(FanOOTD)
class FanOOTDAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'sort_order')
    list_filter = ('group',)
    search_fields = ('title', 'summary')
    ordering = ('sort_order', 'id')


# =====================================================
# 17. 出片啦管理
# =====================================================
@admin.register(FanPhotoFeature)
class FanPhotoFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'sort_order')
    list_filter = ('group',)
    search_fields = ('title', 'summary')
    ordering = ('sort_order', 'id')

