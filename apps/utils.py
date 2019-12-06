import hashlib
import json
import random
import time
from functools import wraps

import pendulum
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from apps.cachext import Cached, make_default_key
from apps.constants import DEFAULT_CACHE_TTL


class C(Cached):
    client = cache


cache.cached = C


def get_random_string(
    length=12,
    allowed_chars="abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
):
    """
    创建指定长度的完全不会重复字符串的
    """
    random.seed(
        hashlib.sha256(
            ("%s%s%s" % (random.getstate(), time.time(), "SCRWEWYOURBITCHES")).encode(
                "utf-8"
            )
        ).digest()
    )
    return "".join(random.choice(allowed_chars) for i in range(length))


def get_long_random_string():
    return get_random_string(24)


def get_short_random_string():
    return get_random_string(12)


def traffic_format(traffic):
    if traffic < 1024 * 8:
        return str(int(traffic)) + "B"

    if traffic < 1024 * 1024:
        return str(round((traffic / 1024.0), 1)) + "KB"

    if traffic < 1024 * 1024 * 1024:
        return str(round((traffic / (1024.0 * 1024)), 1)) + "MB"

    return str(round((traffic / 1073741824.0), 1)) + "GB"


def reverse_traffic(str):
    """
    将流量字符串转换为整数类型
    """
    if "GB" in str:
        num = float(str.replace("GB", "")) * 1024 * 1024 * 1024
    elif "MB" in str:
        num = float(str.replace("MB", "")) * 1024 * 1024
    elif "KB" in str:
        num = float(str.replace("KB", "")) * 1024
    else:
        num = num = float(str.replace("B", ""))
    return round(num)


def simple_cached_view(key=None, ttl=None):
    def decorator(func):
        @wraps(func)
        def cached_view(*args, **kw):
            cache_key = key if key else make_default_key(func, *args, **kw)
            cache_ttl = ttl if ttl else DEFAULT_CACHE_TTL
            resp = cache.get(cache_key)
            if resp:
                return resp
            else:
                resp = func(*args, **kw)
                cache.set(cache_key, resp, cache_ttl)
                return resp

        return cached_view

    return decorator


def authorized(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.method == "GET":
            token = request.GET.get("token", "")
        else:
            data = json.loads(request.body)
            token = data.get("token", "")
            request.json = data
        if token == settings.TOKEN:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({"ret": -1, "msg": "auth error"})

    return wrapper


def api_authorized(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.GET.get("token", "")
        if token != settings.TOKEN:
            return JsonResponse({"msg": "auth error"})
        return view_func(request, *args, **kwargs)

    return wrapper


def handle_json_post(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kw):
        if request.method == "POST":
            request.json = json.loads(request.body)
        return view_func(request, *args, **kw)

    return wrapper


def get_current_time():
    return pendulum.now(tz=settings.TIME_ZONE)
