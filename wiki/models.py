from django.db import models


# =====================================================
# 1. 团体模型
# =====================================================
class IdolGroup(models.Model):
    name = models.CharField("团队名称", max_length=100)
    debut_date = models.DateField("出道日期")
    company = models.CharField("所属公司", max_length=100)
    description = models.TextField("团体简介")
    group_photo = models.ImageField("团体大合照", upload_to='groups/')

    class Meta:
        verbose_name = "偶像团体"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# =====================================================
# 2. 成员主模型
# =====================================================
class Member(models.Model):
    group = models.ForeignKey(
        'IdolGroup',
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name="所属团体"
    )
    stage_name = models.CharField("艺名", max_length=100)
    name = models.CharField("本名", max_length=100)
    birthday = models.DateField("生日")
    position = models.CharField("队内担当", max_length=100)
    mbti = models.CharField("MBTI", max_length=4, blank=True)
    photo = models.ImageField("成员封面主图", upload_to='members/')

    class Meta:
        verbose_name = "成员"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.stage_name


# =====================================================
# 3. 成员自述图片
# =====================================================
class MemberSelfIntro(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='self_intros',
        verbose_name="所属成员"
    )
    image = models.ImageField("自述图/简历图", upload_to='member_self_intro/')
    title = models.CharField("图片标题", max_length=100, blank=True)

    class Meta:
        verbose_name = "成员自述图片"
        verbose_name_plural = "成员自述图片集"

    def __str__(self):
        return f"{self.member.stage_name} - 自述图"


# =====================================================
# 4. 成员个人相册（旧系统，仍然保留）
# =====================================================
class MemberGallery(models.Model):
    CATEGORY_CHOICES = [
        ('WEVERSE', 'Weverse 动态'),
        ('STAGE', '舞台直击'),
        ('AIRPORT', '机场街拍'),
        ('OTHER', '其他日常'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="所属成员"
    )
    image = models.ImageField("相册照片", upload_to='member_gallery/')
    category = models.CharField(
        "照片分类",
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='OTHER'
    )

    class Meta:
        verbose_name = "个人照片"
        verbose_name_plural = "个人相册"

    def __str__(self):
        return f"{self.member.stage_name} - {self.get_category_display()}"


# =====================================================
# 5. 成员直拍
# =====================================================
class MemberFancam(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='fancams',
        verbose_name="所属成员"
    )
    title = models.CharField("直拍舞台名", max_length=200)
    video_url = models.CharField("嵌入链接(src内容)", max_length=500)
    cover = models.ImageField("视频封面", upload_to='fancam_covers/', null=True, blank=True)

    class Meta:
        verbose_name = "个人直拍"
        verbose_name_plural = "精彩直拍视频流"

    def __str__(self):
        return f"{self.member.stage_name} - {self.title}"


# =====================================================
# 6. 专辑模型
# =====================================================
class Album(models.Model):
    group = models.ForeignKey(
        IdolGroup,
        on_delete=models.CASCADE,
        related_name='albums',
        verbose_name="所属团体"
    )
    title = models.CharField("专辑名称", max_length=200)
    cover = models.ImageField("专辑封面", upload_to='albums/')
    release_date = models.DateField("发行日期")

    # 完整音乐跳转链接
    music_url = models.URLField("完整音乐链接", blank=True)

    # 试听设置
    preview_audio = models.FileField(
        "试听音频",
        upload_to='album_previews/',
        blank=True,
        null=True
    )
    preview_start = models.PositiveIntegerField("试听开始秒数", default=0)
    preview_duration = models.PositiveIntegerField("试听时长", default=15)

    class Meta:
        verbose_name = "专辑"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# =====================================================
# 7. 歌曲模型
# =====================================================
class Song(models.Model):
    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name='songs',
        verbose_name="所属专辑"
    )
    title = models.CharField("歌曲名称", max_length=200)
    order = models.IntegerField("曲序", default=1)

    class Meta:
        verbose_name = "歌曲"
        verbose_name_plural = verbose_name
        ordering = ['order']

    def __str__(self):
        return self.title


# =====================================================
# 8. 官方物料系列
# =====================================================
class MediaSeries(models.Model):
    CATEGORY_CHOICES = [
        ('MV', 'MV'),
        ('SHORT', '短视频'),
        ('VARIETY', '综艺'),
        ('BEHIND', '幕后花絮'),
        ('LIVE', '直播'),
        ('SPECIAL', '特别内容'),
        ('OTHER', '其他'),
    ]

    group = models.ForeignKey(
        IdolGroup,
        on_delete=models.CASCADE,
        related_name='media_series',
        verbose_name="所属团体"
    )
    title = models.CharField("系列名称", max_length=200)
    category = models.CharField("物料分类", max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    cover = models.ImageField("系列封面", upload_to='media_series/')
    description = models.TextField("系列简介", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "官方物料系列"
        verbose_name_plural = "官方物料系列"
        ordering = ['category', 'sort_order', 'id']

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"


# =====================================================
# 9. 官方物料单集
# =====================================================
class OfficialMedia(models.Model):
    series = models.ForeignKey(
        MediaSeries,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="所属系列"
    )
    title = models.CharField("单集标题", max_length=200)
    cover = models.ImageField("单集封面", upload_to='official_media/covers/')
    video_url = models.URLField("视频链接", max_length=500)
    description = models.TextField("简介", blank=True)
    release_date = models.DateField("发布日期", null=True, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "官方物料"
        verbose_name_plural = "官方物料"
        ordering = ['sort_order', '-release_date']

    def __str__(self):
        return self.title


# =====================================================
# 10. 活动模型（新相册系统的分类核心）
# =====================================================
class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('comeback', 'wvs自拍'),
        ('music_show', '打歌'),
        ('fanmeeting', '见面会'),
        ('variety', '综艺'),
        ('airport', '机场'),
        ('other', 'Weverse'),
    ]

    group = models.ForeignKey(
        'IdolGroup',
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="所属团体"
    )
    title = models.CharField("活动名称", max_length=200)
    event_type = models.CharField("活动类型", max_length=20, choices=EVENT_TYPE_CHOICES, default='other')
    date = models.DateField("日期", null=True, blank=True)
    cover = models.ImageField("封面", upload_to='events/covers/', blank=True, null=True)
    description = models.TextField("描述", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "活动"
        verbose_name_plural = "活动"
        ordering = ['-date', '-id']

    def __str__(self):
        return self.title


# =====================================================
# 11. 相册图片模型（新系统，单张上传版）
# =====================================================
class Photo(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name="所属活动"
    )

    # 注意：这里 related_name 不能再叫 photos，
    # 因为 MemberGallery 已经占用了 Member.photos
    members = models.ManyToManyField(
        'Member',
        blank=True,
        related_name='album_photos',
        verbose_name="相关成员"
    )

    image = models.ImageField("图片", upload_to='photos/')
    caption = models.CharField("说明", max_length=255, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "活动图片"
        verbose_name_plural = "活动图片"
        ordering = ['-id']

    def __str__(self):
        return f"{self.event.title} - {self.id}"
    

    # =====================================================
# 12. 行程模型（Schedule）
# 用来记录团体在不同时间点的公开行程
# 后续可用于：
# - 首页时间轴
# - 地图打点
# - 已去过 / 即将去 的状态展示
# =====================================================
class Schedule(models.Model):
    # 行程类型
    SCHEDULE_TYPE_CHOICES = [
        ('performance', '演出'),
        ('fanmeeting', '见面会'),
        ('fansign', '签售'),
        ('airport', '机场'),
        ('recording', '录制'),
        ('festival', '音乐节'),
        ('other', '其他'),
    ]

    # 行程状态
    STATUS_CHOICES = [
        ('past', '已结束'),
        ('current', '进行中'),
        ('upcoming', '即将开始'),
    ]

    # 所属团体
    group = models.ForeignKey(
        'IdolGroup',
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="所属团体"
    )

    # 行程标题
    title = models.CharField("行程标题", max_length=200)

    # 行程日期
    date = models.DateField("日期")

    # 城市 / 国家
    city = models.CharField("城市", max_length=100)
    country = models.CharField("国家", max_length=100)

    # 场地（可选）
    venue = models.CharField("场地", max_length=200, blank=True)

    # 行程类型
    schedule_type = models.CharField(
        "行程类型",
        max_length=20,
        choices=SCHEDULE_TYPE_CHOICES,
        default='other'
    )

    # 当前状态
    status = models.CharField(
        "状态",
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    # 地图坐标（后续世界地图会用到）
    latitude = models.FloatField("纬度", null=True, blank=True)
    longitude = models.FloatField("经度", null=True, blank=True)

    # 额外说明
    description = models.TextField("说明", blank=True)

    # 排序字段（可选）
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "团体行程"
        verbose_name_plural = "团体行程"
        ordering = ['date', 'sort_order', 'id']

    def __str__(self):
        return f"{self.date} - {self.title}"


# =====================================================
# 13. 中国平台官方账号
# 用于首页展示团体在中国开通的平台账号
# =====================================================
class ChinaSocialAccount(models.Model):
    PLATFORM_CHOICES = [
        ('xiaohongshu', '小红书'),
        ('bilibili', '哔哩哔哩'),
        ('weibo', '微博'),
        ('douyin', '抖音'),
        ('other', '其他'),
    ]

    group = models.ForeignKey(
        IdolGroup,
        on_delete=models.CASCADE,
        related_name='china_social_accounts',
        verbose_name="所属团体"
    )
    platform = models.CharField("平台", max_length=30, choices=PLATFORM_CHOICES)
    account_name = models.CharField("账号名称", max_length=100)
    profile_url = models.URLField("账号链接")
    avatar = models.ImageField("账号头像", upload_to='china_social_accounts/', blank=True, null=True)
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "中国平台账号"
        verbose_name_plural = "中国平台账号"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.account_name}"

# =====================================================
# 14. 摆摊区（微博站子）
# =====================================================
class FanStation(models.Model):
    group = models.ForeignKey(
        IdolGroup,
        on_delete=models.CASCADE,
        related_name='fan_stations',
        verbose_name="所属团体"
    )

    name = models.CharField("站子名称", max_length=100)
    weibo_name = models.CharField("微博账号名", max_length=100)
    weibo_url = models.URLField("微博主页链接")

    avatar = models.ImageField("头像", upload_to='fan_stations/', blank=True, null=True)
    description = models.CharField("简介", max_length=200, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "摆摊区站子"
        verbose_name_plural = "摆摊区站子"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name
    



    # =====================================================
# 15. 烧烤一下（reaction / 解读）
# =====================================================
class FanReaction(models.Model):
    CATEGORY_CHOICES = [
        ('reaction', 'Reaction'),
        ('analysis', '粉丝解读'),
        ('meme', '梗/趣味内容'),
        ('moment', '名场面分析'),
        ('other', '其他'),
    ]

    group = models.ForeignKey(
        IdolGroup,
        on_delete=models.CASCADE,
        related_name='fan_reactions',
        verbose_name="所属团体"
    )

    title = models.CharField("标题", max_length=200)
    category = models.CharField("分类", max_length=30, choices=CATEGORY_CHOICES, default='other')
    cover = models.ImageField("封面图", upload_to='fan_reactions/', blank=True, null=True)
    source_url = models.URLField("原链接")
    summary = models.TextField("简介", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "烧烤一下"
        verbose_name_plural = "烧烤一下"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title



# =====================================================
# 16. 今日出炉（OOTD / 应援穿搭）
# =====================================================
class FanOOTD(models.Model):
    group = models.ForeignKey(
        IdolGroup,
        on_delete=models.CASCADE,
        related_name='fan_ootds',
        verbose_name="所属团体"
    )

    title = models.CharField("标题", max_length=200)
    cover = models.ImageField("封面图", upload_to='fan_ootds/', blank=True, null=True)
    source_url = models.URLField("原链接")
    summary = models.TextField("简介", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "今日出炉"
        verbose_name_plural = "今日出炉"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


# =====================================================
# 17. 出片啦（站姐 / 神图 / 摄影作品）
# =====================================================
class FanPhotoFeature(models.Model):
    group = models.ForeignKey(
        IdolGroup,
        on_delete=models.CASCADE,
        related_name='fan_photo_features',
        verbose_name="所属团体"
    )

    title = models.CharField("标题", max_length=200)
    cover = models.ImageField("封面图", upload_to='fan_photo_features/', blank=True, null=True)
    source_url = models.URLField("原链接")
    summary = models.TextField("简介", blank=True)
    sort_order = models.PositiveIntegerField("排序", default=1)

    class Meta:
        verbose_name = "出片啦"
        verbose_name_plural = "出片啦"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title
