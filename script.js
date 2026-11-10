const articles = [
  {category:"国内",title:"关注国家发展与民生建设：从权威媒体了解国内重要议题",source:"人民日报 / 人民网",time:"演示条目",url:"https://www.people.com.cn/"},
  {category:"国际",title:"关注国际形势与全球治理：通过多方公开报道了解世界动态",source:"新华社",time:"演示条目",url:"https://www.news.cn/"},
  {category:"经济",title:"观察宏观经济与产业发展：关注政策信息和经济运行",source:"中国新闻网",time:"演示条目",url:"https://www.chinanews.com.cn/"},
  {category:"科技",title:"人工智能与科技创新：持续关注前沿技术发展",source:"央视新闻",time:"演示条目",url:"https://news.cctv.com/"},
  {category:"社会",title:"教育、文化与社会民生：关注公共服务和社会生活",source:"光明网",time:"演示条目",url:"https://www.gmw.cn/"},
  {category:"国内",title:"政策发布与公共信息：建议以政府部门和权威媒体原文为准",source:"新华社",time:"演示条目",url:"https://www.news.cn/"}
];

const grid = document.getElementById("newsGrid");
const empty = document.getElementById("emptyState");
const search = document.getElementById("searchInput");
let currentFilter = "all";

function renderNews() {
  const keyword = search.value.trim().toLowerCase();
  const list = articles.filter(item =>
    (currentFilter === "all" || item.category === currentFilter) &&
    (item.title.toLowerCase().includes(keyword) || item.source.toLowerCase().includes(keyword))
  );
  grid.innerHTML = list.map(item => `
    <article class="news-card">
      <div class="card-meta"><span class="category-pill">${item.category}</span><time>${item.time}</time></div>
      <h3>${item.title}</h3>
      <div class="card-bottom"><span>来源：${item.source}</span><a href="${item.url}" target="_blank" rel="noopener noreferrer">访问来源 ↗</a></div>
    </article>`).join("");
  empty.hidden = list.length !== 0;
}

document.getElementById("filters").addEventListener("click", event => {
  const button = event.target.closest("button[data-filter]");
  if (!button) return;
  currentFilter = button.dataset.filter;
  document.querySelectorAll(".filter").forEach(item => item.classList.toggle("active", item === button));
  renderNews();
});
search.addEventListener("input", renderNews);

const now = new Date();
document.getElementById("today").textContent = new Intl.DateTimeFormat("zh-CN", {
  year:"numeric", month:"long", day:"numeric", weekday:"long"
}).format(now);

renderNews();
