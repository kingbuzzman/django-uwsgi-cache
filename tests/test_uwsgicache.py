import os
import sys
import time
import importlib
import pytest

import httpx

TIMEOUT = int(os.getenv("UWSGICACHE_TEST_TIMEOUT", 3))


def assertions(url):
    assert httpx.get(url + "/delete/1").text == "None"
    assert httpx.get(url + "/get/1").text == "None"
    assert httpx.get(url + "/set/1/a").text == "ok"
    assert httpx.get(url + "/get/1").text == "a"
    assert httpx.get(url + "/clear").text == "ok"
    assert httpx.get(url + "/get/1").text == "None"
    assert httpx.get(url + "/set/2/b?timeout=3").text == "ok"
    time.sleep(2)  # 2 * cache-expire-freq
    assert httpx.get(url + "/get/2").text == "b"
    time.sleep(3)  # 1 + 2 * cache-expire-freq
    assert httpx.get(url + "/get/2").text == "None"
    assert httpx.get(url + "/set/3/c?timeout=0").text == "ok"
    time.sleep(2)  # 2 * cache-expire-freq
    assert httpx.get(url + "/get/3").text == "None"
    assert httpx.get(url + "/set/4/d?timeout=None").text == "ok"
    time.sleep(2)  # 2 * cache-expire-freq
    assert httpx.get(url + "/get/4").text == "d"
    assert httpx.get(url + "/add/5/e").text == "True"
    assert httpx.get(url + "/get/5").text == "e"
    assert httpx.get(url + "/add/6/f?timeout=3").text == "True"
    time.sleep(2)  # 2 * cache-expire-freq
    assert httpx.get(url + "/get/6").text == "f"
    time.sleep(3)  # 1 + 2 * cache-expire-freq
    assert httpx.get(url + "/get/6").text == "None"
    assert httpx.get(url + "/add/7/g?timeout=0").text == "True"
    time.sleep(2)  # 2 * cache-expire-freq
    assert httpx.get(url + "/get/7").text == "None"
    assert httpx.get(url + "/add/8/h?timeout=None").text == "True"
    time.sleep(2)  # 2 * cache-expire-freq
    assert httpx.get(url + "/get/8").text == "h"
    assert httpx.get(url + "/get/8").text == "True"


# class _FakeUwsgiCache:
#     def __init__(self):
#         self._store = {}

#     def _now(self):
#         return time.time()

#     def _is_expired(self, key):
#         if key not in self._store:
#             return True
#         value, expires_at = self._store[key]
#         if expires_at is None:
#             return False
#         if self._now() >= expires_at:
#             # expire
#             del self._store[key]
#             return True
#         return False

#     # uwsgi cache API
#     def cache_exists(self, key, server):
#         return key in self._store and not self._is_expired(key)

#     def cache_get(self, key, server):
#         if self._is_expired(key):
#             return None
#         value, _ = self._store[key]
#         return value

#     def cache_update(self, key, value_bytes, timeout, server):
#         if timeout is None:
#             expires_at = None
#         elif timeout == 0:
#             expires_at = None
#         elif timeout == -1:
#             # expire immediately
#             expires_at = self._now() - 1
#         else:
#             expires_at = self._now() + timeout
#         self._store[key] = (value_bytes, expires_at)

#     def cache_del(self, key, server):
#         existed = key in self._store and not self._is_expired(key)
#         if key in self._store:
#             del self._store[key]
#         return existed

#     def cache_clear(self, server):
#         self._store.clear()


# def _reconfigure_cache_backend(monkeypatch, fallback):
#     # Ensure uwsgicache module reflects desired environment
#     if "uwsgi" in sys.modules:
#         del sys.modules["uwsgi"]
#     if not fallback:
#         sys.modules["uwsgi"] = _FakeUwsgiCache()  # provide fake uwsgi module
#         monkeypatch.delenv("UWSGI_CACHE_FALLBACK", raising=False)
#     else:
#         monkeypatch.setenv("UWSGI_CACHE_FALLBACK", "y")
#     import uwsgicache as uwsgicache_module
#     importlib.reload(uwsgicache_module)
#     # Update Django settings to use the backend
#     from django.core.cache import caches
#     from django.conf import settings as dj_settings
#     dj_settings.CACHES = {"default": {"BACKEND": "uwsgicache.UWSGICache", "LOCATION": "foobar"}}
#     # Clear caches to pick up new backend
#     caches._caches = {}


# def test_uwsgi_backend_with_live_server(live_server, monkeypatch):
#     _reconfigure_cache_backend(monkeypatch, fallback=False)
#     assertions(live_server.url)


@pytest.mark.filterwarnings("ignore")
def test_locmem(live_server):
    # _reconfigure_cache_backend(monkeypatch, fallback=True)
    assertions(live_server.url)
