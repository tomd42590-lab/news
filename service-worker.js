
const CACHE_NAME = "newshub-v1";

const STATIC_FILES = [
  "./",
  "./index.html",
  "./style.css",
  "./script.js",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png"
];

// 安装：缓存应用基础文件
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_FILES);
    })
  );

  self.skipWaiting();
});

// 激活：清理旧版本缓存
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      );
    })
  );

  self.clients.claim();
});

// 请求：新闻数据优先联网，失败时读取缓存
self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);

  if (request.method !== "GET" || url.origin !== self.location.origin) {
    return;
  }

    if (url.pathname.endsWith("/data/news.json")) {
    const cacheKey = new Request(url.origin + url.pathname);

    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(cacheKey, copy);
            });
          }
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(cacheKey);
          return cached || new Response("新闻暂时无法加载", {
            status: 503
          });
        })
    );
    return;
    }

  // 其他静态文件优先使用缓存
  event.respondWith(
    caches.match(request).then(cached => {
      return cached || fetch(request);
    })
  );
});
