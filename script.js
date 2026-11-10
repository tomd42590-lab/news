// 自动统计各栏目新闻数量
function updateCounts() {
  const categories = ["国内", "国际", "经济", "科技", "社会"];

  document.getElementById("count-all").textContent = articles.length;

  categories.forEach(category => {
    const count = articles.filter(
      item => item.category === category
    ).length;

    document.getElementById("count-" + category).textContent = count;
  });
}
let articles = [];

const grid = document.getElementById("newsGrid");
const empty = document.getElementById("emptyState");
const search = document.getElementById("searchInput");

let currentFilter = "all";

async function loadNews() {
  try {
    const response = await fetch("./data/news.json?t=" + Date.now());

    if (!response.ok) {
      throw new Error("新闻数据加载失败：" + response.status);
    }

    const data = await response.json();
    articles = Array.isArray(data) ? data : (data.articles || []);

updateCounts();
renderNews();
    console.log("成功加载新闻：", articles.length, "条");

  } catch (error) {
    console.error(error);
    grid.replaceChildren();

    empty.hidden = false;
    empty.textContent = "新闻加载失败，请稍后刷新页面。";
  }
}

function renderNews() {
  const keyword = search.value.trim().toLowerCase();

  const list = articles.filter(item => {
    const categoryMatch =
      currentFilter === "all" ||
      item.category === currentFilter;

    const searchMatch =
      (item.title || "").toLowerCase().includes(keyword) ||
      (item.source || "").toLowerCase().includes(keyword);

    return categoryMatch && searchMatch;
  });

  grid.replaceChildren();

  list.forEach(item => {
    const card = document.createElement("article");
    card.className = "news-card";

    const meta = document.createElement("div");
    meta.className = "card-meta";

    const category = document.createElement("span");
    category.className = "category-pill";
    category.textContent = item.category || "新闻";

    const time = document.createElement("time");
    const date = new Date(item.pubDate);

    time.textContent = item.pubDate
      ? (isNaN(date.getTime()) ? item.pubDate : date.toLocaleString("zh-CN"))
      : "时间未知";

    meta.append(category, time);

    const title = document.createElement("h3");
    title.textContent = item.title;

    const bottom = document.createElement("div");
    bottom.className = "card-bottom";

    const source = document.createElement("span");
    source.textContent = "来源：" + (item.source || "未知来源");

    const link = document.createElement("a");
    link.textContent = "阅读原文 ↗";

    try {
      const url = new URL(item.link);

      if (url.protocol === "https:" || url.protocol === "http:") {
        link.href = url.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      } else {
        link.textContent = "链接不可用";
      }
    } catch {
      link.textContent = "链接不可用";
    }

    bottom.append(source, link);
    card.append(meta, title, bottom);
    grid.appendChild(card);
  });

  empty.hidden = list.length !== 0;

  if (list.length === 0) {
    empty.textContent = "没有找到匹配的新闻。";
  }
}

// 新闻分类筛选
document.getElementById("filters").addEventListener("click", event => {
  const button = event.target.closest("button[data-filter]");

  if (!button) return;

  currentFilter = button.dataset.filter;

  document.querySelectorAll(".filter").forEach(item => {
    item.classList.toggle("active", item === button);
  });

  renderNews();
});
// 顶部导航和侧边分类入口
document.querySelectorAll(".main-nav a, .side-panel a").forEach(link => {
  link.addEventListener("click", event => {
    const target = link.getAttribute("href");

    // 首页：返回页面顶部
    if (target === "#top") {
      event.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: "smooth"
      });
      return;
    }

    const categoryMap = {
      "#domestic": "国内",
      "#world": "国际",
      "#economy": "经济",
      "#technology": "科技",
      "#society": "社会"
    };

    const category = categoryMap[target];

    if (!category) return;

    event.preventDefault();

    const button = document.querySelector(
      `.filter[data-filter="${category}"]`
    );

    if (button) button.click();

    document.getElementById("domestic").scrollIntoView({
      behavior: "smooth",
      block: "start"
    });
  });
});
// 新闻关键词搜索
search.addEventListener("input", renderNews);

// 显示当前日期
const now = new Date();

document.getElementById("today").textContent =
  new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long"
  }).format(now);

// 加载新闻
loadNews();
// 注册 Service Worker
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("./service-worker.js")
      .then(registration => {
        console.log("NewsHub 离线缓存已启用：", registration.scope);
      })
      .catch(error => {
        console.error("Service Worker 注册失败：", error);
      });
  });
}
