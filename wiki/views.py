import json
from collections import OrderedDict
from django.shortcuts import render, get_object_or_404
from .models import IdolGroup, Member, Album, MediaSeries, Event, Schedule ,ChinaSocialAccount,FanStation,FanReaction, FanOOTD, FanPhotoFeature


# =====================================================
# 1. 首页
# - 展示成员
# - 展示专辑
# - 展示官方物料
# - 展示团体相册（按分类分组）
# - 展示行程时间轴
# - 给世界地图提供点位数据
# - 给世界地图提供国家着色数据
# =====================================================
def index(request):
    group = IdolGroup.objects.first()

    # 防止后台还没建团体时首页直接报错
    if not group:
        context = {
            'group': None,
            'members': [],
            'albums': [],
            'media_series': [],
            'grouped_events': [],
            'schedules': [],
            'schedule_map_points_json': '[]',
            'country_fill_data_json': '[]',
            'china_social_accounts': [],
            'fan_stations': [],
            'fan_reactions': [],
            'fan_ootds': [],
            'fan_photo_features': [],

        }
        return render(request, 'wiki/index.html', context)

    members = Member.objects.filter(group=group)
    albums = Album.objects.filter(group=group).prefetch_related('songs')
    media_series = MediaSeries.objects.filter(group=group).prefetch_related('items')
    china_social_accounts = ChinaSocialAccount.objects.filter(group=group)
    fan_stations = FanStation.objects.filter(group=group)
    fan_reactions = FanReaction.objects.filter(group=group)
    fan_ootds = FanOOTD.objects.filter(group=group)
    fan_photo_features = FanPhotoFeature.objects.filter(group=group)
    events = Event.objects.filter(group=group).prefetch_related('photos').order_by('-date', '-id')
    schedules = Schedule.objects.filter(group=group).order_by('date', 'sort_order', 'id')

    # =================================================
    # 团体相册：按活动类型分组
    # =================================================
    event_type_map = OrderedDict([
        ('comeback', '回归'),
        ('music_show', '打歌'),
        ('fanmeeting', '见面会'),
        ('variety', '综艺'),
        ('airport', '机场'),
        ('other', '其他'),
    ])

    grouped_events = []
    for key, label in event_type_map.items():
        items = [event for event in events if event.event_type == key]
        if items:
            grouped_events.append({
                'key': key,
                'label': label,
                'items': items,
            })

    # =================================================
    # 世界地图点位数据
    # 只有填了经纬度的行程才会上地图
    # ECharts 坐标格式：[经度, 纬度]
    # =================================================
    schedule_map_points = []
    for item in schedules:
        if item.latitude is not None and item.longitude is not None:
            schedule_map_points.append({
                'name': f"{item.city}, {item.country}",
                'title': item.title,
                'city': item.city,
                'country': item.country,
                'date': item.date.strftime('%Y-%m-%d'),
                'status': item.status,
                'value': [float(item.longitude), float(item.latitude)],
            })

    # =================================================
    # 世界地图国家着色数据
    # 用来让“已去过 / 进行中 / 即将去”的国家整块变蓝
    # 注意：国家名要和 world.json 里的英文名匹配
    # =================================================
    country_name_map = {
        '法国': 'France',
        '韩国': 'Korea',
        '日本': 'Japan',
        '中国': 'China',
        '美国': 'United States',
        '英国': 'United Kingdom',
        '德国': 'Germany',
        '意大利': 'Italy',
        '西班牙': 'Spain',
        '加拿大': 'Canada',
        '泰国': 'Thailand',
        '新加坡': 'Singapore',
    }

    status_priority = {
        'past': 1,
        'upcoming': 2,
        'current': 3,
    }

    country_status_map = {}

    for item in schedules:
        if item.country:
            old_status = country_status_map.get(item.country)

            if old_status is None:
                country_status_map[item.country] = item.status
            elif status_priority.get(item.status, 0) > status_priority.get(old_status, 0):
                country_status_map[item.country] = item.status

    country_fill_data = []
    for country, status in country_status_map.items():
        country_fill_data.append({
            'name': country_name_map.get(country, country),
            'status': status,
            'value': 1,
        })

    context = {
        'group': group,
        'members': members,
        'albums': albums,
        'media_series': media_series,
        'grouped_events': grouped_events,
        'schedules': schedules,
        'schedule_map_points_json': json.dumps(schedule_map_points, ensure_ascii=False),
        'country_fill_data_json': json.dumps(country_fill_data, ensure_ascii=False),
        'china_social_accounts': china_social_accounts,
        'fan_stations': fan_stations,
        'fan_reactions': fan_reactions,
        'fan_ootds': fan_ootds,
        'fan_photo_features': fan_photo_features,


    }

    return render(request, 'wiki/index.html', context)


# =====================================================
# 2. 成员详情页
# 只展示新相册系统里和该成员有关的活动相册
# =====================================================
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    group = member.group
    albums = Album.objects.filter(group=group).prefetch_related('songs')

    member_events = Event.objects.filter(
        photos__members=member
    ).prefetch_related('photos', 'photos__members').distinct().order_by('-date', '-id')

    context = {
        'member': member,
        'group': group,
        'albums': albums,
        'member_events': member_events,
    }
    return render(request, 'wiki/member_detail.html', context)


# =====================================================
# 3. 官方物料系列详情页
# =====================================================
def media_series_detail(request, pk):
    series = get_object_or_404(
        MediaSeries.objects.prefetch_related('items'),
        pk=pk
    )

    group = series.group

    context = {
        'series': series,
        'group': group,
        'items': series.items.all(),
    }
    return render(request, 'wiki/media_series_detail.html', context)


# =====================================================
# 4. 团体相册总页
# =====================================================
def gallery_view(request):
    events = Event.objects.prefetch_related('photos', 'photos__members').order_by('-date', '-id')

    context = {
        'events': events,
    }
    return render(request, 'wiki/gallery.html', context)
